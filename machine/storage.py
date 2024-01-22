from typing import Optional


class Product:
    prod_id: int
    name: Optional[str]
    price: Optional[float]

    def __init__(self, prod_id, name=None, price=None):
        self.prod_id = prod_id
        self.name = name
        self.price = price


class Storage:
    def __init__(self):
        self.products: dict[int, Product] = {}
        self.slots: dict[int, tuple[int, int]] = {}
        self.slots_ids: dict[int, int] = {}

    def initialize(self, data):
        products = data.get('products', [])
        slots = data.get('slots', [])
        for prod in products:
            self.update_product(prod['id'], prod['name'], prod['price'])

        for slot in slots:
            self.update_storage(slot['id'], slot['slot'], slot['product'], slot['amount'])

    def update_product(self, prod_id: int, name: str, price: float):
        if prod_id in self.products:
            prod = self.products[prod_id]
            prod.name = name
            prod.price = price
        else:
            self.products[prod_id] = Product(prod_id, name, price)

    def update_storage(self, slot_id: int, slot: int, prod_id: int, qty: int):
        if slot_id in self.slots_ids and self.slots_ids[slot_id] != slot:
            slot_nr = self.slots_ids[slot_id]
            del self.slots[slot_nr]
        if qty == 0 and slot in self.slots:
            del self.slots[slot]
            del self.slots_ids[slot_id]
        elif qty > 0:
            self.slots[slot] = prod_id, qty
            self.slots_ids[slot_id] = slot

    def perform_transaction(self, slot: int, prod_id: int):
        if slot in self.slots and self.slots[slot][0] == prod_id:
            self.slots[slot] = prod_id, self.slots[slot][1] - 1

    def products_list(self) -> list[tuple[Product, int]]:
        return [(self.products[prod_id], slot) for slot, (prod_id, qty) in self.slots.items() if qty > 0]
