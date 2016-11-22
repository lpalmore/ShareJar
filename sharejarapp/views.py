from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forms import UserForm, AddBalanceForm, AddCharityForm, CreateTeamForm, JoinTeamForm, InviteTeamForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from .forms import MakePaymentForm
from paypalrestsdk import Payment
from paypal import createPayment, executePayment
from django.shortcuts import redirect
from team_helpers import addMemberToTeam, generateCode



def createUser(request):
    #if post request, create the new user
    if request.method == "POST":
        form = UserForm(request.POST)
        print form.is_valid()
        if form.is_valid():
            user = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            newUser = User.objects.create_user(user, email, password)
            newUser.save() #so there will not be multiple users
            # Create derived member
            member = Member(user=newUser,
                            paypal_email=form.cleaned_data['paypalEmail'])
            member.save()
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

#no corresponding page for this...
@login_required
def addCharity(request):
    current_user = request.user
    message = ""
    #if post request, add charity
    if request.method == 'POST':
        member = Member.objects.get(user=current_user)
        form = AddCharityForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            charityname= form.cleaned_data['charityname']
            print charityname
            description = form.cleaned_data['description']
            paypal_email = form.cleaned_data['paypal_email']
            Charity.objects.create(charityname=charityname, description=description, paypal_email=paypal_email)
            message = str(charityname) + " charity has been added!"
            #charity added
            #else:
            #message = "Please enter a charity that has not already been added"

    #create form for adding charity
    #not letting me do this
    form = AddCharityForm()
    template = loader.get_template('sharejarapp/addCharity.html')
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
    current_user = request.user
    member = Member.objects.get(user=current_user)
    currentTeam = None
    currentTeamObject = None
    try:
        currentTeamObject = TeamMemberList.objects.get(member=member).team
        currentTeam = currentTeamObject.name
    except ObjectDoesNotExist:
        pass
    if request.method == 'POST':
        #Determine which form was submitted
        if 'create_team' in request.POST:
            form = CreateTeamForm(request.POST)
            if form.is_valid():
                #Add team with this name to the DB
                newTeamObject = Team.objects.create(name=form.cleaned_data['name'])
                newTeamObject.save()
                addMemberToTeam(member, newTeamObject, currentTeamObject)
                currentTeam = newTeamObject.name
            else:
                print "Create Team Form Error!"
        elif 'join_team' in request.POST:
            form = JoinTeamForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                try:
                    inviteObject = Invite.objects.get(code=form.cleaned_data['code'])
                    if current_user.email == inviteObject.email:
                        #Add this user to the team
                        newTeamObject = inviteObject.team
                        addMemberToTeam(member, newTeamObject, currentTeamObject)
                        inviteObject.delete()
                        currentTeam = newTeamObject
                    else:
                        # Code does not match this user's email
                        pass
                except ObjectDoesNotExist:
                    pass
            else:
                #form error
                pass
        elif 'invite_member' in request.POST:
            # Generate code, associate code with email
            form = InviteTeamForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                inviteObject = Invite.objects.create(team=currentTeamObject, code=generateCode(), email=email)
                #Send a notification and code to email provided
            else:
                pass
        else:
            pass #Error!
    context = {'currentTeam': currentTeam}
    #Does this member have an outstanding balance?
    outstandingBalances = None
    try:
        outstandingBalances = Balances.objects.filter(member=member).aggregate(Sum('balance'))
        outstandingBalances = outstandingBalances['balance__sum']
    except ObjectDoesNotExist:
        pass
    if outstandingBalances == None or outstandingBalances == 0:
        #This user may create or join a new team
        context['createTeamForm'] = CreateTeamForm()
        context['joinTeamForm'] = JoinTeamForm()
    else:
        print "You have outstanding balances!" + str(outstandingBalances)

    if currentTeam:
        #This user may invite new people to the team
        context['inviteTeamForm'] = InviteTeamForm()
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
        template = loader.get_template('sharejarapp/makepayment.html')
        context = {"charity": charity, "paymentForm":MakePaymentForm()}
    return HttpResponse(template.render(context, request))

def confirmPayment(request, etc):
    payerID = request.GET.get('PayerID', '')
    paymentID = request.GET.get('paymentId', '')
    print 'payerID: ' + payerID
    print 'paymentID: ' + paymentID
    current_user = request.user
    member = Member.objects.get(user=current_user)
    success = executePayment(payerID, paymentID, member)
    template = loader.get_template('sharejarapp/confirmPayment.html')
    context = {
        'success': success
    }
    return HttpResponse(template.render(context, request))