from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return f"Product {self.id}: {self.name}"

class Vmachine(models.Model):
    identifier = models.CharField(max_length=255, primary_key=True, blank=False)
    address = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=255, blank=True)
    token = models.CharField(max_length=255, null=False, unique=True, db_index=True)

    def __str__(self):
        return f"machine {self.identifier}"
    

class Slot(models.Model):
    id = models.AutoField(primary_key=True)
    vmachine_fk = models.ForeignKey('Vmachine', on_delete=models.CASCADE, verbose_name='machine')
    product_fk = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name='product')
    slot_number = models.IntegerField(null=False)
    amount = models.IntegerField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['vmachine_fk', 'slot_number'], name='unique_slot')
        ]

    def __str__(self):
        return f"{self.id}: Slot {self.slot_number} in {self.vmachine_fk} - Product: {self.product_fk}, Amount: {self.amount}"    


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    card_nr = models.CharField(max_length=255, null=False, unique=True, verbose_name='card number')
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE, null=False, verbose_name='user')

    active = models.BooleanField(default=False)
    funds = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f"{self.id}: User {self.user_fk} - Active: {self.active}, Funds: {self.funds}"


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    user_fk = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='user')
    vmachine_fk = models.ForeignKey(Vmachine, on_delete=models.SET_NULL, null=True, verbose_name='machine')
    product_fk = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='product')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    transaction_time = models.DateTimeField(null=False)

    def __str__(self):
        return f"{self.id}: {self.transaction_time} User {self.user_fk} paid: {self.price}"

