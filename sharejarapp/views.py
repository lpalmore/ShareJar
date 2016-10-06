from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forms import UserForm
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
    #get input
    increment = 1
    #get user
    current_user = request.user

    #FIXLATER update balance for that user
    b = Balances.objects.get(user=current_user)
    b.balance += increment
    b.save()
    #if balance update is successful
    success = True
    balance = b.balance

    template = loader.get_template('sharejarapp/addBalance.html')
    context = {
        'success': success,
        'balance': balance
    }
    return HttpResponse(template.render(context, request))

@login_required
def currentBalance(request):
    #get user from db
    user = "hello"
    #FIXLATER return actual username
    #get balance for user
    balance = 6
    #FIXLATER RETURN actual balance
    #pass template to browser
    template = loader.get_template('sharejarapp/currentBalance.html')
    #Example context for this template
    context = {
        'balances': [('charityname1', 20), ('charityname2', 12)]
    }
    return HttpResponse(template.render(context, request))

@login_required
def joinTeam(request):
    template = loader.get_template('sharejarapp/joinTeam.html')
    context = {
    }
    return HttpResponse(template.render(context, request))
