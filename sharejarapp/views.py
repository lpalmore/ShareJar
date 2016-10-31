from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forms import UserForm, AddBalanceForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from models import Balances, Member, Charity
from django.core.exceptions import ObjectDoesNotExist

from .forms import MakePaymentForm
from paypalrestsdk import Payment
from paypal import createPayment, executePayment
from django.shortcuts import redirect



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
            # Create derived member
            member = Member(user=newUser,
                            paypal_email=form.cleaned_data['paypalEmail'])
            member.save()
            print "Success "
            return HttpResponseRedirect('login')
            #add balance of zero for new user
            #balance = Balances(user=newUser, balance=0)
            #balance.save()
            #print balance
    else:
        form = UserForm()
        print "Error"
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
        member = Member.objects.get(user=current_user)
        form = AddBalanceForm(request.POST)
        if form.is_valid():
            increment = form.cleaned_data['increment']
            charityname= form.cleaned_data['charity']
            #get user
            #update balance for that user
            if increment >= 0:
                b = None
                try:
                    b = Balances.objects.get(member=member, charity=charityname)
                    b.balance += increment
                    b.save()
                except ObjectDoesNotExist:
                    b = Balances.objects.create(member=member, charity=charityname, balance=increment)
                message = str(increment) + " has been added!"
            #balance added
            else:
                message = "Please enter a positive value"

    #create form for adding balance
    form = AddBalanceForm()
    template = loader.get_template('sharejarapp/addBalance.html')
    context = {
        'form': form
        }

    return HttpResponse(template.render(context, request))

@login_required
def currentBalance(request):
    
    #get user from db
    # return actual username
    #get balance for user
    current_user = request.user
    member = Member.objects.get(user=current_user)
    b = None
    try:
        b = Balances.objects.all().filter(member=member)
    except ObjectDoesNotExist:
        pass
    #balance = b.balance
    #pass template to browser
    #Example context for this template
    context = {
        'balances': b
    }
    template = loader.get_template('sharejarapp/currentBalance.html')
    return HttpResponse(template.render(context, request))

@login_required
def joinTeam(request):
    template = loader.get_template('sharejarapp/joinTeam.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def makePayment(request, charity):
    # TODO Actually pull the balance from the model
    if request.method == 'POST':
        form = MakePaymentForm(request.POST)
        if form.is_valid():
            current_user = request.user
            memberEmail = Member.objects.get(user=current_user).paypal_email
            charityEmail = Charity.objects.get(charityname=charity).paypal_email
            amount = form.cleaned_data['amount']
            redirectURL = createPayment(memberEmail, amount, charity, charityEmail)
            if redirectURL:
                return redirect(redirectURL)
            else:
                return redirect('/addBalance/')
                pass
        else:
            # Form data isn't valid. Notify the user
            pass
    else:
        template = loader.get_template('sharejarapp/makePayment.html')
        context = {"charity": charity, "paymentForm":MakePaymentForm()}
    return HttpResponse(template.render(context, request))

def confirmPayment(request, charity):
    payerID = request.GET.get('PayerID', '')
    paymentID = request.GET.get('paymentId', '')
    print 'payerID: ' + payerID
    print 'paymentID: ' + paymentID
    current_user = request.user
    success = executePayment(payerID, paymentID, Member.objects.get(user=current_user))
    template = loader.get_template('sharejarapp/confirmPayment.html')
    context = {
    }
    return HttpResponse(template.render(context, request))