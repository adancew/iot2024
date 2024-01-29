from django import forms
from .models import Product


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class EnterCardForm(forms.Form):
    card_nr = forms.CharField(max_length=65)
    username = forms.CharField(max_length=65)
    active = forms.BooleanField(required = False)
    funds = forms.FloatField()

class EnterProductForm(forms.Form):
    price = forms.FloatField()
    name = forms.CharField(max_length=65)

class EnterClientForm(forms.Form):
    username = forms.CharField(max_length=65)
    first_name = forms.CharField(max_length=65)
    last_name = forms.CharField(max_length=65)
    email = forms.EmailField()

class EnterVmachineForm(forms.Form):
    identifier = forms.CharField()
    address = forms.CharField()
    description = forms.CharField()
    token = forms.CharField()

class EnterSlotForm(forms.Form):
    product = forms.ChoiceField(choices=[(p.name, p.name) for p in Product.objects.all()]) 
    slot_number = forms.IntegerField()
    amount = forms.IntegerField()

class DeleteForm(forms.Form):
    pass # no fields, only buttons