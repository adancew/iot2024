import logging

from paho.mqtt import client as mqtt

from .transaction import TransactionService
from .transaction import Result


class MQTTCommunicator:
    client: mqtt.Client
    transactions: TransactionService

    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger(__name__)
        client.on_message = self.on_message
        client.on_connect = self.on_connect

    def on_message(self, _client, _userdata, msg):
        self.handle_message(msg)

    @staticmethod
    def on_connect(client, _userdata, _flags, _rc):
        client.subscribe('transaction/#')
        client.subscribe('balance-request/#')

    def handle_message(self, msg):
        self.logger.info(f'MQTT message received: {msg.topic} -- {msg.payload}')
        if msg.topic.startswith('transaction/'):
            try:
                machine_id, card = msg.topic.removeprefix('transaction/').split('/')
                slot_nr, prod_id, timestamp = msg.payload.decode('utf-8').split(';')
                slot_nr = int(slot_nr)
                prod_id = int(prod_id)
                timestamp = int(timestamp)
            except ValueError:
                pass
            else:
                self.transactions.perform_transaction(machine_id, card, slot_nr, prod_id, timestamp)
        elif msg.topic.startswith('balance-request/'):
            card = msg.topic.removeprefix('balance-request/')
            self.transactions.request_balance(card)

    def storage_change(self, machine: str, slot_id: int, slot: int, prod_id: int, qty: int):
        self.client.publish(f'storage/{machine}/{slot_id}', f'{slot};{prod_id};{qty}'.encode('utf-8'))

    def product_change(self, prod_id: int, name: str, price: float):
        self.client.publish(f'products/{prod_id}', f'{name};{price:.2f}'.encode('utf-8'))

    def transaction_result(self, machine_id: str, card_nr: str, result: Result):
        self.client.publish(f'transaction-result/{machine_id}/{card_nr}', str(result.value).encode('utf-8'))

    def balance(self, card_nr: str, result: Result, balance: float = 0.0):
        self.client.publish(f'balance/{card_nr}', f'{result.value};{balance:.2f}'.encode('utf-8'))
