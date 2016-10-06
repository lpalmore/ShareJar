from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forms import UserForm, AddBalanceForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from models import Balances


def createUser(request):
    #if post request, create the new user
    if request.method == "POST":
        form = UserForm(request.POST)
        print form.is_valid()
        if form.is_valid():
            user = form.cleaned_data['username']
            print user;
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            newUser = User.objects.create_user(user, email, password)
            #add balance of zero for new user
            balance = Balances(user=newUser, balance=0)
            balance.save()
            print balance
            return HttpResponseRedirect('login')
    else:
        form = UserForm()
    template = loader.get_template('registration/createUser.html')
    context = {
        'form': form,
    }
    return HttpResponse(template.render(context, request))

@login_required
def home(request):
    template = loader.get_template('sharejarapp/index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def teamStats(request):
    template = loader.get_template('sharejarapp/teamStats.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def addBalance(request):
    current_user = request.user
    message = ""
    #if post request, add increment
    if request.method == 'POST':
        form = AddBalanceForm(request.POST)
        if form.is_valid():
            increment = form.cleaned_data['increment']
            #get user
            #update balance for that user
            if increment >= 0:
                b = Balances.objects.get(user=current_user)
                b.balance += increment
                b.save()
                message = str(increment) + " has been added!"
            #balance added
            else:
                message = "Please enter a positive value"
    b = Balances.objects.get(user=current_user)
    balance = b.balance
    #create form for adding balance
    form = AddBalanceForm()
    template = loader.get_template('sharejarapp/addBalance.html')
    context = {
        'balance': balance,
        'form': form,
        'message': message,
    }
    return HttpResponse(template.render(context, request))

@login_required
def currentBalance(request):
    #get user from db
    # return actual username
    #get balance for user
    current_user = request.user
    b = Balances.objects.get(user=current_user)
    balance = b.balance
    #pass template to browser
    template = loader.get_template('sharejarapp/currentBalance.html')
    context = {
        'balance': balance
    }
    return HttpResponse(template.render(context, request))

@login_required
def joinTeam(request):
    template = loader.get_template('sharejarapp/joinTeam.html')
    context = {
    }
    return HttpResponse(template.render(context, request))
