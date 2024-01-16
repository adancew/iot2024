from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"Product {self.id}: {self.description}"
    
class Vmachine(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"machine {self.id}"
    

class Slot(models.Model):
    id = models.AutoField(primary_key=True)
    vmachine_fk = models.ForeignKey('Vmachine', on_delete=models.CASCADE)
    product_fk = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    slot_number = models.IntegerField(null=False)
    amount = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.id}: Slot {self.slot_number} in {self.vmachine_fk} - Product: {self.product_fk}, Amount: {self.amount}"    
    


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    funds = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f"{self.id}: User {self.user_fk} - Active: {self.active}, Funds: {self.funds}"


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    user_fk = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vmachine_fk = models.ForeignKey(Vmachine, on_delete=models.SET_NULL, null=True)
    product_fk = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    transaction_time = models.DateTimeField(null=False)

    def __str__(self):
        return f"{self.id}: {self.transaction_time} User {self.user_fk} paid: {self.price}"

