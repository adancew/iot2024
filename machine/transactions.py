from enum import Enum
from typing import TYPE_CHECKING, Optional

from storage import Storage, Product
from gui import Menu, BalanceRead, PurchaseRequest

if TYPE_CHECKING:
    from mqtt import MQTTCommunicator
    


class Result(Enum):
    OK = 0
    NOT_ENOUGH_MONEY = 1
    NOT_ENOUGH_PRODUCTS = 2
    NOT_ACTIVE_CARD = 3
    UNKNOWN_PRODUCT = 4
    UNKNOWN_CARD = 5
    UNKNOWN_ERROR = 6


class TransactionManager:
    mqtt: 'MQTTCommunicator'
    storage: Storage
    card: Optional[str] = None
    slot: Optional[int] = None
    product: Optional[Product] = None
    menu: 'Menu'

    def __init__(self, storage):
        self.storage = storage

    def request_balance(self, card: str):
        print('balance')
        self.card = card
        self.mqtt.balance_request(card)

    def start_transaction(self, slot: int, product: Product):
        self.slot = slot
        self.product = product

    def commit_transaction(self, card: str):
        self.card = card
        self.mqtt.transaction_commit(card, self.slot, self.product.prod_id)

    def cancel_transaction(self):
        self.card = None
        self.slot = None
        self.product = None

    def process_balance(self, result: Result, card: str, balance: float):
        if card != self.card:
            return
        self.card = None
        if isinstance(self.menu.state, BalanceRead):
            self.menu.state.balance(balance)

    def process_transaction_result(self, card: str, result: Result):
        if card != self.card:
            return
        self.card = None
        if result == Result.OK:
            self.storage.perform_transaction(self.slot, self.product.prod_id)
        if isinstance(self.menu.state, PurchaseRequest):
            self.menu.purchase(result)
        self.slot = None
        self.product = None
