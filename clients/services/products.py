from typing import TYPE_CHECKING

from django.db.models.signals import post_save

from clients.models import Product

if TYPE_CHECKING:
    from .mqtt_communicator import MQTTCommunicator


class ProductService:
    mqtt: 'MQTTCommunicator'

    def __init__(self, mqtt: 'MQTTCommunicator'):
        self.mqtt = mqtt
        post_save.connect(self.on_product_change, Product, weak=False)

    def on_product_change(self, instance: Product, **_kwargs):
        self.mqtt.product_change(instance.id, instance.name, float(instance.price))

    @staticmethod
    def get_products():
        return [
            {
                'id': prod.id,
                'name': prod.name,
                'price': float(prod.price)
            }
            for prod in Product.objects.all()
        ]

