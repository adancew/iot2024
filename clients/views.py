from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group

from .utils import is_owner
from .forms import *
from .models import *


def sign_in(request):

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dash')
        
        form = LoginForm()
        return render(request,'clients/login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password=form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                return redirect('dash')
        
        # either form not valid or user is not authenticated
        messages.error(request,f'Invalid username or password')
        return render(request,'clients/login.html',{'form': form})
    

def sign_out(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('login')     


@login_required
def dash(request):
    if request.user.is_staff:
        return render(request, 'clients/owner_dash.html')
    else:
        user_cards = Card.objects.filter(user_fk=request.user.id)
        user_transactions = Transaction.objects.filter(user_fk=request.user.id)
        context = {"transactions": user_transactions, "cards": user_cards}
        return render(request, 'clients/user_dash.html', context)
    
    

# MANAGING TRANSACTIONS
@user_passes_test(is_owner)
def transactions(request):
    return render(request,'clients/transactions_index.html',
                  {'transactions':Transaction.objects.all()})

# MANAGING CARDS    
@user_passes_test(is_owner)
def cards(request):
    return render(request,'clients/cards_index.html',
                  {'cards':Card.objects.all()})

@user_passes_test(is_owner)
def cards_add(request):
    if request.method == 'POST':

        form = EnterCardForm(request.POST)
       
        if form.is_valid():
            new_card = Card(
                card_nr=form.cleaned_data['card_nr'],
                user_fk= User.objects.get(username=form.cleaned_data['username']),
                funds=form.cleaned_data['funds'],
                active= 'active' in form.cleaned_data,
            )
            new_card.save()
           
            messages.success(request, "dodano nową kartę")
            return redirect('card-add')      
    else:
        form = EnterCardForm()
        
    return render(request, 'clients/resource_add.html', 
                  {'form': form, 'resource_name':"Karty", 'resource_addr':'cards' })

@user_passes_test(is_owner)
def cards_edit(request, card_id):
    card=Card.objects.get(id=card_id)
    if request.method == 'POST':
        
        form = EnterCardForm(request.POST, 
                             initial= {
                                 'card_nr':card.card_nr,
                                 'username':card.user_fk,
                                 'funds':card.funds,
                                })
       
        if form.is_valid():
            card.card_nr=form.cleaned_data['card_nr']
            card.user_fk=User.objects.get(username=form.cleaned_data['username'])
            card.funds=form.cleaned_data['funds']
            card.active=form.cleaned_data['active']
            card.save()
            messages.success(request, "edytowano kartę")
            return redirect('card-index')  
           
    else:
        form = EnterCardForm(initial= {
                                 'card_nr':card.card_nr,
                                 'username':card.user_fk,
                                 'funds':card.funds,
                                 'active':card.active
                             })
        
    return render(request, 'clients/resource_edit.html', 
                 {'form': form, 'resource_name':"Karty", 'resource_addr':'cards' })

@user_passes_test(is_owner)
def cards_delete(request, card_id):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            try:
                card = Card.objects.get(id=card_id)
                card.delete()
                messages.success(request, "Usuwanie zakończyło się sukcesem.")
            except:
                messages.error(request, "Usuwanie nie powiodło się.")
            return redirect('card-index')
                    
    else:
        form = DeleteForm()

    return render(request, 'clients/delete_confirm.html', 
                  {'form': form, 'resource_name':"Kartę", 'resource_addr':'cards' })


# MANAGING PRODUCTS
@user_passes_test(is_owner)
def products(request):
    return render(request,'clients/products_index.html',
                  {'products':Product.objects.all()})

@user_passes_test(is_owner)
def products_add(request):
    if request.method == 'POST':

        form = EnterProductForm(request.POST)
       
        if form.is_valid():
            new_product = Product(
                price=form.cleaned_data['price'],
                name=form.cleaned_data['name'],
            )
            new_product.save()
           
            messages.success(request, "dodano nowy produkt")
            return redirect('product-add')      
    else:
        form = EnterProductForm()
        
    return render(request, 'clients/resource_add.html', 
                   {'form': form, 'resource_name':"Produktu", 'resource_addr':'products' })

@user_passes_test(is_owner)
def products_edit(request, product_id):
    product=Product.objects.get(id=product_id)
    if request.method == 'POST':
        
        form = EnterProductForm(request.POST, 
                             initial= {
                                 'price':product.price,
                                 'name':product.name,
                                })
       
        if form.is_valid():
            product.price=form.cleaned_data['price']
            product.name=form.cleaned_data['name']
            product.save()
            messages.success(request, "edytowano produkt")
            return redirect('product-index')  
           
    else:
        form = EnterProductForm(initial= {
                                'price':product.price,
                                'name':product.name,
                                })
        
    return render(request, 'clients/resource_edit.html', 
                  {'form': form, 'resource_name':"Produktu", 'resource_addr':'products' })

@user_passes_test(is_owner)
def products_delete(request, product_id):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            try:
                product = Product.objects.get(id=product_id)
                product.delete()
                messages.success(request, "Usuwanie zakończyło się sukcesem.")
            except:
                messages.error(request, "Usuwanie nie powiodło się.")
            return redirect('product-index')
                    
    else:
        form = DeleteForm()

    return render(request, 'clients/delete_confirm.html', 
                  {'form': form, 'resource_name':"Produkt", 'resource_addr':'products' })


# MANAGING CLIENTS
@user_passes_test(is_owner)
def clients(request):
    return render(request,'clients/clients_index.html',
                  {'clients':User.objects.filter(is_staff=False)})

@user_passes_test(is_owner)
def clients_add(request):
    if request.method == 'POST':

        form = EnterClientForm(request.POST)
       
        if form.is_valid():
            new_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'], 
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password="clientclient",
                is_staff=False) # TODO find a way to handle defualt passwords
            #new_user.groups.add(Group.objects.get(name="Clients"))
            new_user.save()
            messages.success(request, "dodano nowego klienta")
            return redirect('client-add')      
    else:
        form = EnterClientForm()
        
    return render(request, 'clients/resource_add.html', 
                   {'form': form, 'resource_name':"Klienta", 'resource_addr':'clients' })

@user_passes_test(is_owner)
def clients_edit(request, client_id):
    client = User.objects.get(id=client_id)
    if request.method == 'POST':

        form = EnterClientForm(request.POST, 
                             initial= {
                                 'username':client.username,
                                 'first_name':client.first_name,
                                 'last_name':client.last_name,
                                 'email':client.email,
                                })
       
        if form.is_valid():
            client.username=form.cleaned_data['username']
            client.first_name=form.cleaned_data['first_name']
            client.last_name=form.cleaned_data['last_name']
            client.email=form.cleaned_data['email']
            client.save()
            messages.success(request, "edytowano klienta")
            return redirect('client-index')  
           
    else:
        form = EnterClientForm(initial= {
                                'username':client.username,
                                'first_name':client.first_name,
                                'last_name':client.last_name,
                                'email':client.email,
                                })
        
    return render(request, 'clients/resource_edit.html', 
                  {'form': form, 'resource_name':"Klienta", 'resource_addr':'clients' })

@user_passes_test(is_owner)
def clients_delete(request, product_id):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            try:
                client = User.objects.get(id=product_id)
                client.delete()
                messages.success(request, "Usuwanie zakończyło się sukcesem.")
            except:
                messages.error(request, "Usuwanie nie powiodło się.")
            return redirect('client-index')
                    
    else:
        form = DeleteForm()

    return render(request, 'clients/delete_confirm.html', 
                  {'form': form, 'resource_name':"Klienta", 'resource_addr':'clients' })


# MANAGING VENDING MACHINES
@user_passes_test(is_owner)
def vmachines(request):
    return render(request,'clients/vmachines_index.html',
                  {'vmachines':Vmachine.objects.all()})

@user_passes_test(is_owner)
def vmachines_edit(request, vmachine_id):
    vmachine = Vmachine.objects.get(identifier= vmachine_id)
    if request.method == 'POST':

        form = EnterVmachineForm(request.POST, 
                               initial= {
                                 'identifier':vmachine.identifier,
                                 'address':vmachine.address,
                                 'description':vmachine.description,
                                 'token':vmachine.token,
                                })
       
        if form.is_valid():
            vmachine.identifier=form.cleaned_data['identifier']
            vmachine.address=form.cleaned_data['address']
            vmachine.description=form.cleaned_data['description']
            vmachine.save()
            messages.success(request, "edytowano automat")
            return redirect('vmachine-index')  
           
    else:
        form = EnterVmachineForm(initial= {
                                 'identifier':vmachine.identifier,
                                 'address':vmachine.address,
                                 'description':vmachine.description,
                                 'token':vmachine.token,
                                })
        
    return render(request, 'clients/vmachine_edit.html', 
                  {'form': form, 'slots':Slot.objects.filter(vmachine_fk=vmachine.identifier) })

@user_passes_test(is_owner)
def vmachines_add(request):
    if request.method == 'POST':
        form = EnterVmachineForm(request.POST)
       
        if form.is_valid():
            vmachine=Vmachine(
                identifier=form.cleaned_data['identifier'],
                address=form.cleaned_data['address'],
                description=form.cleaned_data['description'],
                token=form.cleaned_data['token'],
                )
            vmachine.save()
            messages.success(request, "dodano automat")
            return redirect('vmachine-index')  
           
    else:
        form = EnterVmachineForm()
        
    return render(request, 'clients/resource_add.html', 
                  {'form': form, 'resource_name':"Automatu", 'resource_addr':'vmachines' })

@user_passes_test(is_owner)
def vmachines_delete(request, vmachine_id):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            try:
                vmachine = Vmachine.objects.get(identifier=vmachine_id)
                vmachine.delete()
                messages.success(request, "Usuwanie zakończyło się sukcesem.")
            except:
                messages.error(request, "Usuwanie nie powiodło się.")
            return redirect('vmachine-index')
                    
    else:
        form = DeleteForm()

    return render(request, 'clients/delete_confirm.html', 
                  {'form': form, 'resource_name':"Automat", 'resource_addr':'vmachines' })


# MANAGE SLOTS
@user_passes_test(is_owner)
def slots_add(request, vmachine_id):
    vmachine = Vmachine.objects.get(identifier= vmachine_id)
    
    if request.method == 'POST':

        form = EnterSlotForm(request.POST)
       
        if form.is_valid():
            slot = Slot(
                vmachine_fk = Vmachine.objects.get(identifier=vmachine_id),
                product_fk = Product.objects.get(name=form.cleaned_data['product']),
                slot_number = form.cleaned_data['slot_number'],
                amount = form.cleaned_data['amount'])
            slot.save()
            messages.success(request, "dodano slot")
            return redirect('vmachine-edit', vmachine_id)  
           
    else:
        form = EnterSlotForm()
       
    return render(request, 'clients/resource_add.html', 
                  {'form': form, 
                   'resource_addr':('vmachines/'+str(vmachine_id)+'/edit/'),
                   'resource_name':'slotu',
                   'slots': Slot.objects.filter(vmachine_fk=vmachine.identifier),
                   'products': Product.objects.all() })


@user_passes_test(is_owner)
def slots_edit(request, vmachine_id, slot_id):
    vmachine = Vmachine.objects.get(identifier= vmachine_id)
    slot = Slot.objects.get(id= slot_id)
    
    if request.method == 'POST':

        form = EnterSlotForm(request.POST, 
                               initial= {
                                 'product':slot.product_fk,
                                 'amount':slot.amount,
                                })
       
        if form.is_valid():
            slot.product_fk = Product.objects.get(name=form.cleaned_data['product'])
            slot.amount = form.cleaned_data['amount']
            slot.save()
            messages.success(request, "edytowano slot")
            return redirect('vmachine-edit', vmachine_id)  
           
    else:
        form = EnterSlotForm(initial= {
                                 'product':slot.product_fk,
                                 'amount':slot.amount,
                                })
       
    return render(request, 'clients/resource_edit.html', 
                  {'form': form, 
                   'resource_addr':('vmachines/'+str(vmachine_id)+'/edit'),
                   'resource_name':'slotu',
                   'slots': Slot.objects.filter(vmachine_fk=vmachine.identifier),
                   'products': Product.objects.all() })


@user_passes_test(is_owner)
def slots_delete(request, vmachine_id, slot_id):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            try:
                slot = Slot.objects.get(id=slot_id)
                slot.delete()
                messages.success(request, "Usuwanie zakończyło się sukcesem.")
            except:
                messages.error(request, "Usuwanie nie powiodło się.")
            return redirect('vmachine-edit', vmachine_id)
                    
    else:
        form = DeleteForm()

    return render(request, 'clients/delete_confirm.html', 
                  {'form': form, 
                   'resource_name':"slot", 
                   'resource_addr':'vmachines/'+str(vmachine_id)+'/edit/' })

