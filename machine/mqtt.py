from paho.mqtt import client as mqtt

from configuration import MACHINE_ID, BROKER_IP
from storage import Storage
from transactions import TransactionManager
from utils import Result


class MQTTCommunicator:
    client: mqtt.Client
    storage: Storage
    transaction_manager: TransactionManager

    def __init__(self, client, storage, transaction_manager):
        self.client = client
        self.storage = storage
        self.transaction_manager = transaction_manager

    def on_message(self, _client, _userdata, msg):
        self.handle_message(msg)

    @staticmethod
    def on_connect(client, _userdata, _flags, _rc):
        client.subscribe('products/#')
        client.subscribe(f'storage/{MACHINE_ID}/#')

    def handle_message(self, msg):
        print(msg.topic, msg.payload)
        if msg.topic.startswith('products/'):
            try:
                prod_id = int(msg.topic.removeprefix('products/'))
                name, price = msg.payload.decode('utf-8').split(';')
                price = float(price)
            except ValueError:
                pass
            else:
                self.storage.update_product(prod_id, name, price)
        elif msg.topic.startswith('storage/'):
            try:
                slot_id = int(msg.topic.removeprefix(f'storage/{MACHINE_ID}/'))
                slot, prod_id, qty = msg.payload.decode('utf-8').split(';')
                slot = int(slot)
                prod_id = int(prod_id)
                qty = int(qty)
            except ValueError:
                pass
            else:
                self.storage.update_storage(slot_id, slot, prod_id, qty)
        elif msg.topic.startswith('balance/'):
            self.client.unsubscribe(msg.topic)
            card = msg.topic.removeprefix('balance/')
            try:
                result, _, balance = msg.payload.decode('utf-8').partition(';')
                result = Result(int(result))
                if result == Result.OK:
                    balance = float(balance)
                else:
                    balance = 0.0
            except ValueError:
                pass
            else:
                self.transaction_manager.process_balance(result, card, balance)

        elif msg.topic.startswith('transaction-result/'):
            self.client.unsubscribe(msg.topic)
            try:
                machine_id, card = msg.topic.removeprefix('transaction-result/').split('/')
                if machine_id != MACHINE_ID:
                    return
                result = int(msg.payload.decode('utf-8'))
                result = Result(result)
            except ValueError:
                pass
            else:
                self.transaction_manager.process_transaction_result(card, result)

    def balance_request(self, card: str, time: int):
        self.client.subscribe(f'balance/{card}')
        self.client.publish(f'balance-request/{card}', str(time).encode('utf-8'))

    def transaction_commit(self, card: str, slot: int, product: int, time: int):
        self.client.subscribe(f'transaction-result/{MACHINE_ID}/{card}')
        self.client.publish(f'transaction/{MACHINE_ID}/{card}',
                            f'{slot};{product};{time}'.encode('utf-8'))


def start_mqtt(storage, transaction_manager):
    client = mqtt.Client(MACHINE_ID, clean_session=False)
    comm = MQTTCommunicator(client, storage, transaction_manager)
    client.on_message = comm.on_message
    client.on_connect = comm.on_connect
    client.connect(BROKER_IP)

    client.loop_start()
    return comm



