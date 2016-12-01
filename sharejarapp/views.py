from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from forms import UserForm, AddBalanceForm, CharityForm, CreateTeamForm, JoinTeamForm, InviteTeamForm, LookupCharityForm, EditCharityForm, LookupUserForm, ChangeTeamNameForm, LeaveTeamForm, EditBalanceForm, ChangeLeaderForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from models import Balances, Member, Charity, Team, TeamMemberList, Invite, Admin, Donation
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.urls import reverse

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .forms import MakePaymentForm
from paypalrestsdk import Payment
from paypal import createPayment, executePayment
from django.shortcuts import redirect


from team_helpers import addMemberToTeam, GetTeams, leaveTeam, isLeader, getUsernamesInTeam, EditTeamMemberBalance, getAllTeamBalances, transferLeader, editTeamName
from balance_helpers import getBalance, addToBalance

def admin_check(user):
    try:
        admin = Admin.objects.get(user=user)
        return True
    except ObjectDoesNotExist:
        return False

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
    current_user = request.user
    try:
        admin = Admin.objects.get(user=current_user)
        template = loader.get_template('sharejarapp/adminIndex.html')
    except ObjectDoesNotExist:
        template = loader.get_template('sharejarapp/index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def teamStats(request, teamName=None):
    if teamName is None:
        teams = Team.objects.all()
        template = loader.get_template('sharejarapp/teamStats.html')
        context = { 'teams': teams }
        return HttpResponse(template.render(context, request))
    else:
        print "Team name:" + teamName
        team = None
        donationTotal = None
        allMemberDonationList = None
        currentMembers = None
        context = {'teamName':teamName}
        try:
            team = Team.objects.get(name=teamName)
            # Sum of every donation made by members (former and present) of this team
            donationTotal = Donation.objects.filter(team=team).aggregate(Sum('total'))
            allMemberDonationList = Donation.objects.filter(team=team)
            currentMembers = TeamMemberList.objects.filter(team=team).values_list('member', flat=True)
            currentMembers = Member.objects.filter(pk__in=currentMembers).all()
        except ObjectDoesNotExist:
            print "\n Failed to find donation information \n"

        if donationTotal['total__sum'] == None:
            donationTotal = 0
        else:
            donationTotal = donationTotal['total__sum']

        context['donationTotal'] = donationTotal
        if allMemberDonationList and currentMembers:
            print "\n\n\n WTF"
            print currentMembers
            currentMemberDonations = [ob for ob in allMemberDonationList if ob.member in currentMembers]
            formerMemberDonations = [ob for ob in allMemberDonationList if ob.member not in currentMembers]

            if currentMemberDonations:
                context['currentMemberDonations'] = currentMemberDonations
            if formerMemberDonations:
                context['formerMemberDonations'] = formerMemberDonations
        else:
            print "No Donations to show"

        template = loader.get_template('sharejarapp/teamStatsSpecific.html')
        return HttpResponse(template.render(context, request))

@login_required
def balance(request):
    current_user = request.user

    if request.method == "POST":
        member = Member.objects.get(user=current_user)
        form = AddBalanceForm(request.POST)
        if form.is_valid():
            increment = form.cleaned_data['increment']
            charityname= form.cleaned_data['charity']
            addToBalance(member, charityname, increment)
    #get balance info and create add balance form
    balances = getBalance(current_user)
    form = AddBalanceForm()

    template = loader.get_template('sharejarapp/balance.html')
    context = {
        'balances': balances,
        'form': form
    }
    return HttpResponse(template.render(context, request))

@login_required
def joinTeam(request):
    context = {}
    template = loader.get_template('sharejarapp/joinTeam.html')
    current_user = request.user
    member = Member.objects.get(user=current_user)

    context['createTeamForm'] = CreateTeamForm()
    context['inviteTeamForm'] = InviteTeamForm()
    context['changeTeamNameForm'] = ChangeTeamNameForm()
    context['joinTeamForm'] = JoinTeamForm(member=member)

    #process all post requests
    if request.method == 'POST':
        #Determine which form was submitted
        if 'create_team' in request.POST:
            createTeamForm = CreateTeamForm(request.POST)
            print createTeamForm
            if createTeamForm.is_valid():
                #Add team with this name to the DB
                newTeamObject = Team.objects.create(name=createTeamForm.cleaned_data['name'], leader=member)
                newTeamObject.save()
                addMemberToTeam(member, newTeamObject, None)
            else:
                context['createTeamForm'] = createTeamForm
        elif 'join_team' in request.POST:
            form = JoinTeamForm(request.POST, member=member)
            if form.is_valid():
                teamName = form.cleaned_data['team']
                try:
                    team = Team.objects.get(name=teamName)
                    inviteObject = Invite.objects.get(member=member, team=team)
                    newTeamObject = inviteObject.team
                    addMemberToTeam(member, newTeamObject, None)
                    inviteObject.delete()
                except ObjectDoesNotExist:
                    pass
            else:
                #form error
                pass
        elif 'invite_member' in request.POST:
            # Generate code, associate code with email
            form = InviteTeamForm(request.POST)
            if form.is_valid():
                team = form.cleaned_data['team']
                username = form.cleaned_data['username']
                try:
                    inviteUser = User.objects.get(username=username)
                    inviteMember = Member.objects.get(user=inviteUser)
                    #TODO invite form needs to send team
                    inviteToTeam = Team.objects.get(name=team)
                    inviteObject = Invite.objects.create(team=inviteToTeam, member=inviteMember)
                except ObjectDoesNotExist:
                    pass # Error
                #Send a notification and code to email provided
            else:
                pass
        elif 'leave_team' in request.POST:
            leaveTeamForm = LeaveTeamForm(request.POST)
            if leaveTeamForm.is_valid():
                teamToLeave = leaveTeamForm.cleaned_data['team']
                leaveTeam(teamToLeave, member)
        elif 'edit_balance' in request.POST:
            editBalanceForm = EditBalanceForm(request.POST)
            print editBalanceForm
            if editBalanceForm.is_valid():
                edit_balance_member = editBalanceForm.cleaned_data['member']
                edit_balance_charity = request.POST['charity'].split('_')[1]
                edit_balance_amount = request.POST['amount']
                EditTeamMemberBalance(edit_balance_member, edit_balance_charity, edit_balance_amount)
        elif 'change_leader' in request.POST:
            changeLeaderForm = ChangeLeaderForm()
            if changeLeaderForm.is_valid():
                newLeader = changeLeaderForm.cleaned_data['NewTeamLeader']
                teamToChange = changeLeaderForm.cleaned_data['team']
                transferLeader(teamToChange, newLeader)
        elif 'change_team_name' in request.POST:
            formCTN = ChangeTeamNameForm(request.POST)
            if formCTN.is_valid():
                newTeamName = formCTN.cleaned_data['name']
                currentTeam = formCTN.cleaned_data['team']
                editTeamName(currentTeam, newTeamName)
            else:
                pass
        else:
            pass #Error!

    #retrieve teams information
    teams = GetTeams(member)
    TeamsInfo = []
    for t in teams:
        teamInfo = {}
        if t.leader == member:
            membernames = getUsernamesInTeam(t)
            teamInfo['membernames'] = membernames
            memberbalances = getAllTeamBalances(t)
            teamInfo['memberbalances'] = memberbalances
            #add choose charity here
        TeamsInfo.append((t, teamInfo))
    context["TeamsInfo"] = TeamsInfo
    context["hasTeam"] = (len(teams) != 0)
    context["username"] = member.user.username


    ''' Do we still want to not allow people with outstandng balances from joining a team?
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
        context['inviteTeamForm'] = InviteTeamForm()
        context['changeTeamNameForm'] = ChangeTeamNameForm()
        context['joinTeamForm'] = JoinTeamForm(member=member)
    else:
        print "You have outstanding balances!" + str(outstandingBalances)
    '''

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

@login_required
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


@user_passes_test(admin_check)
def addCharity(request):
    current_user = request.user
    message = ""
    #if post request, add charity
    if request.method == 'POST':
        form = CharityForm(request.POST)
        if form.is_valid():
            charityname= form.cleaned_data['charityname']
            description = form.cleaned_data['description']
            paypal_email = form.cleaned_data['paypal_email']
            charity = Charity.objects.create(charityname=charityname, description=description, paypal_email=paypal_email)
            charity.save()
            return HttpResponseRedirect(reverse('adminHome'))
    else:
        form = CharityForm()
    template = loader.get_template('sharejarapp/addCharity.html')
    context = {
        'form': form
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(admin_check)
def lookupCharity(request):
    hasSearched = False
    if request.method == 'POST':
        hasSearched = True
        form = LookupCharityForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['charityname']
            charities = Charity.objects.all().filter(charityname=name)
            template = loader.get_template('sharejarapp/lookupCharity.html')
            context = {
                'form': form,
                'charities': charities
            }
            return HttpResponse(template.render(context, request))
    else:
        form = LookupCharityForm()
        template = loader.get_template('sharejarapp/lookupCharity.html')
        context = {
            'hasSearched': hasSearched,
            'form': form
        }
        return HttpResponse(template.render(context, request))

@user_passes_test(admin_check)
def editCharity(request, charityName):
    charity = Charity.objects.get(charityname=charityName)
    if request.method == 'POST':
        form = EditCharityForm(request.POST)
        if form.is_valid():
            charityname= form.cleaned_data['charityname']
            description = form.cleaned_data['description']
            paypal_email = form.cleaned_data['paypal_email']
            if (charityname != ''):
                charity.charityname = charityname
            if (description != ''):
                charity.description = description
            if (paypal_email != ''):
                charity.paypal_email = paypal_email
            charity.save()
    else:
        form = EditCharityForm()
    template = loader.get_template('sharejarapp/editCharity.html')
    context = {
        'form': form,
        'charity': charity
    }
    return HttpResponse(template.render(context, request))


@user_passes_test(admin_check)
def removeCharity(request):
    hasSearched = False
    if request.method == 'POST':
        hasSearched = True
        form = LookupCharityForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['charityname']
            charities = Charity.objects.all().filter(charityname=name)
            template = loader.get_template('sharejarapp/removeCharity.html')
            context = {
                'form': form,
                'charities': charities
            }
            return HttpResponse(template.render(context, request))
    else:
        form = LookupCharityForm()
        template = loader.get_template('sharejarapp/removeCharity.html')
        context = {
            'form': form,
            'hasSearched': hasSearched
        }
        return HttpResponse(template.render(context, request))

@user_passes_test(admin_check)
def confirmRemoveCharity(request, charityName):
    charity = Charity.objects.get(charityname=charityName)
    if request.GET.get('confirm'):
        Balances.objects.all().filter(charity=charity).delete()
        charity.delete()
        return HttpResponseRedirect(reverse('adminHome'))
    template = loader.get_template('sharejarapp/confirmRemoveCharity.html')
    context = {
        'charity': charity
    }
    return HttpResponse(template.render(context, request))

@user_passes_test(admin_check)
def deleteAccount(request):
    if request.method == 'POST':
        form = LookupUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.all().filter(username=username)
            members = Member.objects.all().filter(user=user)
            template = loader.get_template('sharejarapp/deleteAccount.html')
            context = {
                'form': form,
                'members': members
            }
            return HttpResponse(template.render(context, request))
    else:
        form = LookupUserForm()
        template = loader.get_template('sharejarapp/deleteAccount.html')
        context = {
            'form': form
        }
        return HttpResponse(template.render(context, request))

@user_passes_test(admin_check)
def confirmDeleteAccount(request, username):
    user = User.objects.get(username=username)
    account = Member.objects.get(user=user)
    if request.GET.get('confirm'):
        #TeamMemberList.objects.all().filter(member=account).delete()
        Balances.objects.all().filter(member=account).delete()
        #account.delete()
        return HttpResponseRedirect(reverse('adminHome'))
    template = loader.get_template('sharejarapp/confirmDeleteAccount.html')
    context = {
        'member': account
    }
    return HttpResponse(template.render(context, request))



@user_passes_test(admin_check)
def editBalance(request):
    template = loader.get_template('sharejarapp/editBalance.html')
    context = {
    }
    return HttpResponse(template.render(context, request))
