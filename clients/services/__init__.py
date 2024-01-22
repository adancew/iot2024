from paho.mqtt import client as mqtt

from vending.settings import BROKER_IP
from .machines import MachineService
from .mqtt_communicator import MQTTCommunicator
from .products import ProductService
from .storage import StorageService
from .transaction import TransactionService

__all__ = [
    'MachineService',
    'MQTTCommunicator',
    'ProductService',
    'StorageService',
    'TransactionService',
    'run'
]


def run():
    client = mqtt.Client()
    client.connect(BROKER_IP)
    comm = MQTTCommunicator(client)
    ProductService(comm)
    storage_srv = StorageService(comm)
    comm.transactions = TransactionService(comm, storage_srv)
    

    client.loop_start()
