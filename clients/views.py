from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from .forms import LoginForm
from .models import Transaction, Product, Card


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
    if request.user.groups.filter(name="Owners").exists():
        return render(request,'clients/owner_dash.html',{})
    elif request.user.groups.filter(name="Clients").exists():
        user_cards = Card.objects.filter(user_fk=request.user.id)
        user_transactions =  Transaction.objects.filter(user_fk=request.user.id)
        context = {"transactions":user_transactions, "cards": user_cards}
        return render(request,'clients/user_dash.html',context)
    else:
        return render(request,'clients/empty_dash.html',{})