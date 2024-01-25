from typing import TYPE_CHECKING

from django.db.models.signals import post_save, post_delete, pre_save

from clients.models import Slot

if TYPE_CHECKING:
    from .mqtt_communicator import MQTTCommunicator


class StorageService:
    mqtt: 'MQTTCommunicator'

    def __init__(self, mqtt: 'MQTTCommunicator'):
        self.mqtt = mqtt
        post_save.connect(self.on_slot_change, Slot, weak=False)
        post_delete.connect(self.on_slot_delete, Slot, weak=False)

    def on_slot_change(self, instance: Slot, **_kwargs):
        self.mqtt.storage_change(instance.vmachine_fk.identifier, instance.id, instance.slot_number,
                                 instance.product_fk.id, instance.amount)

    def on_slot_delete(self, instance: Slot, **_kwargs):
        self.mqtt.storage_change(instance.vmachine_fk.identifier, instance.id, instance.slot_number,
                                 instance.product_fk.id, 0)

    @staticmethod
    def perform_transaction(machine_id: str, slot_nr: int, product_id: int, qty: int = 1) -> bool:
        slot = Slot.objects.get(vmachine_fk__identifier=machine_id, slot_number=slot_nr)
        if slot and slot.product_fk.id == product_id and slot.amount >= 1:
            # slot.save()
            slot.amount -= qty
            return True
        return False

    @staticmethod
    def get_slots(machine_id: str):
        return [
            {
                'id': slot.id,
                'slot': slot.slot_number,
                'product': slot.product_fk.id,
                'amount': slot.amount
            } for slot in Slot.objects.filter(vmachine_fk__identifier=machine_id)
        ]
