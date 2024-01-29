import logging
from enum import Enum
from typing import TYPE_CHECKING

from django.db import transaction

from .log import LoggingService
from .storage import StorageService
from ..models import Card, Product

if TYPE_CHECKING:
    from .mqtt_communicator import MQTTCommunicator


class Result(Enum):
    OK = 0
    NOT_ENOUGH_MONEY = 1
    NOT_ENOUGH_PRODUCTS = 2
    NOT_ACTIVE_CARD = 3
    UNKNOWN_PRODUCT = 4
    UNKNOWN_CARD = 5
    UNKNOWN_ERROR = 6


class TransactionService:
    mqtt: 'MQTTCommunicator'
    storage: StorageService

    def __init__(self, mqtt: 'MQTTCommunicator', storage: StorageService):
        self.mqtt = mqtt
        self.storage = storage
        self.logger = logging.getLogger(__name__)


    @staticmethod
    def get_card(card_nr: str) -> Card:
        return Card.objects.filter(card_nr=card_nr).first()

    def perform_transaction(self, machine_id: str, card_nr: str,
                            slot_nr: int, prod_id: int, timestamp: int):
        try:
            card = self.get_card(card_nr)
            if not card:
                self.logger.info(f'Transaction attempt with unknown card {card_nr}')
                self.mqtt.transaction_result(machine_id, card_nr, Result.UNKNOWN_CARD)
                return
            if not card.active:
                self.logger.info(f'Transaction attempt with inactive card {card_nr}')
                self.mqtt.transaction_result(machine_id, card_nr, Result.NOT_ACTIVE_CARD)
                return
            product = Product.objects.filter(id=prod_id).first()
            if not product:
                self.logger.info(f'Transaction attempt with unknown product {prod_id}')
                self.mqtt.transaction_result(machine_id, card_nr, Result.UNKNOWN_PRODUCT)
                return

            with transaction.atomic():
                if not self.storage.perform_transaction(machine_id, slot_nr, prod_id):
                    self.logger.info(f'Transaction attempt with not enough products {prod_id} in slot {slot_nr}')
                    self.mqtt.transaction_result(machine_id, card_nr, Result.NOT_ENOUGH_PRODUCTS)
                    return
                card.funds -= product.price
                card.save()
                LoggingService.log_transaction(card, product, machine_id, timestamp)

            self.mqtt.transaction_result(machine_id, card_nr, Result.OK)
            self.logger.info(f'Transaction performed with card {card_nr} and product {prod_id}')
        except Exception as e:
            self.logger.error(f'Error during transaction: {e}')
            import traceback
            traceback.print_exc()
            self.mqtt.transaction_result(machine_id, card_nr, Result.UNKNOWN_ERROR)

    def request_balance(self, card_nr: str):
        try:
            card = self.get_card(card_nr)
            if not card:
                self.logger.info(f'Balance request with unknown card {card_nr}')
                self.mqtt.balance(card_nr, Result.UNKNOWN_CARD)
                return
            if not card.active:
                self.logger.info(f'Balance request with inactive card {card_nr}')
                self.mqtt.balance(card_nr, Result.NOT_ACTIVE_CARD)
                return
            self.mqtt.balance(card_nr, Result.OK, float(card.funds))
            self.logger.info(f'Balance request performed with card {card_nr}')
        except Exception as e:
            self.logger.error(f'Error during balance request: {e}')
            self.mqtt.balance(card_nr, Result.UNKNOWN_ERROR)
