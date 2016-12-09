from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from forms import *
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from models import Balances, Member, Charity, Team, TeamMemberList, Invite, Admin, Donation
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.urls import reverse
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.generic import View
from .forms import MakePaymentForm
from paypalrestsdk import Payment
from paypal import createPayment, executePayment
from django.shortcuts import redirect
from team_helpers import addMemberToTeam, GetTeams, leaveTeam, isLeader, getUsernamesInTeam, EditTeamMemberBalance, getAllTeamBalances, transferLeader, editTeamName
from balance_helpers import getAllBalance, getTeamBalance, addToTeamBalance, addToBalance


def admin_check(user):
    try:
        admin = Admin.objects.get(user=user)
        return True
    except ObjectDoesNotExist:
        return False

#admin can add charity information
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

#admin can search for a charity
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

#admin can edit charity details
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

#admin can remove a charity
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

#admin confirms deletion of a charity
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

#admin can delete account
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

#admin confirms deletion of an account
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



#payment confirmation after payal
class ConfirmPaymentView(View):
    template_name = 'sharejarapp/confirmPayment.html'
    def get(self, request, etc):
        teamName = etc[1:]
        payerID = request.GET.get('PayerID', '')
        paymentID = request.GET.get('paymentId', '')
        member = Member.objects.get(user=request.user)
        success = executePayment(payerID, paymentID, member, teamName)
        return render(request, self.template_name, {'sucess': success})

#make a donation through payal
class MakePaymentView(View):
    template_name = 'sharejarapp/makepayment.html'
    balance = None
    def setInfo(self, user, charity, team):
        member = Member.objects.get(user=user)
        if team:
            teamObj = Team.objects.get(name=team)
            self.balance = Balances.objects.get(member=member, team=teamObj)
        else:
            charityObj = Charity.objects.get(charityname=charity)
            self.balance = Balances.objects.get(member=member, charity=charityObj, team=None)
        return
    def get(self, request, charity, team=None):
        self.setInfo(request.user, charity, team)
        context = {"charity": charity, "balance": self.balance, "paymentForm":MakePaymentForm()}
        if team:
            context['team'] = team
        return render(request, self.template_name, context)
    def post(self, request, charity, team):
        self.setInfo(request.user, charity, team)
        form = MakePaymentForm(request.POST)
        if form.is_valid():
            memberEmail = Member.objects.get(user=request.user).paypal_email
            charityEmail = Charity.objects.get(charityname=charity).paypal_email
            amount = form.cleaned_data['amount']
            if team:
                redirectURL = createPayment(memberEmail, amount, charity, charityEmail, team)
            else:
                redirectURL = createPayment(memberEmail, amount, charity, charityEmail)
            if redirectURL:
                return redirect(redirectURL)
            else:
                return redirect('/balances/')

#displays breakdown of each team's contributions
class TeamStatsView(View):
    template_name = 'sharejarapp/teamStats.html'
    def get(self, request, teamName=None):
        if teamName is None:
            teams = Team.objects.all()
            return render(request, self.template_name, { 'teams': teams })
        else:
            self.template_name = 'sharejarapp/teamStatsSpecific.html'
            # Display team stats about the given team
            team, donationTotal, allMemberDonationList, currentMembers = None, None, None, None
            context = {'teamName':teamName}
            try:
                team = Team.objects.get(name=teamName)
                # Sum of every donation made by members (former and present) of this team
                donationTotal = Donation.objects.filter(team=team).aggregate(Sum('total'))
                allMemberDonationList = Donation.objects.filter(team=team)
                currentMembers = TeamMemberList.objects.get(team=team).members.all()
            except ObjectDoesNotExist:
                print "\n Failed to find donation information \n"
            if donationTotal['total__sum'] == None:
                donationTotal = 0
            else:
                donationTotal = donationTotal['total__sum']
            context['donationTotal'] = donationTotal
            if allMemberDonationList and currentMembers:
                # Sort into two lists which Donations are from former members, and
                # which are from current members
                currentMemberDonations = [ob for ob in allMemberDonationList if ob.member in currentMembers]
                formerMemberDonations = [ob for ob in allMemberDonationList if ob.member not in currentMembers]

                if currentMemberDonations:
                    context['currentMemberDonations'] = currentMemberDonations
                if formerMemberDonations:
                    context['formerMemberDonations'] = formerMemberDonations
            else:
                print "No Donations to show"
            return render(request, self.template_name, context)

class CreateUserView(View):
    template_name = 'registration/createUser.html'
    def get(self, request):
        form = UserForm()
        return render(request, self.template_name, {'form': form})
    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            newUser = User.objects.create_user(data['username'], data['email'], data['password'])
            newUser.save()
            member = Member(user=newUser, paypal_email=data['paypalEmail'])
            member.save()
            return HttpResponseRedirect('login')
        else:
            return get(request)

#all functionality used by a team (changing leadership, updating balances, inviting members)
class JoinTeamView(View):
    template_name = 'sharejarapp/joinTeam.html'
    context = {}
    def addBlankForms(self, member):
        self.context['createTeamForm'] = CreateTeamForm()
        self.context['inviteTeamForm'] = InviteTeamForm()
        self.context['changeTeamNameForm'] = ChangeTeamNameForm()
        self.context['joinTeamForm'] = JoinTeamForm(member=member)
    def generateTeamInfo(self, member):
        teams = GetTeams(member)
        TeamsInfo = []
        for t in teams:
            teamInfo = {}
            if t.leader == member:
                membernames = getUsernamesInTeam(t)
                teamInfo['membernames'] = membernames
                memberbalances = getAllTeamBalances(t)
                teamInfo['memberbalances'] = memberbalances
            TeamsInfo.append((t, teamInfo))
        self.context["TeamsInfo"] = TeamsInfo
        self.context["hasTeam"] = (len(teams) != 0)
        self.context["username"] = member.user.username
    def get(self, request):
        current_user = request.user
        member = Member.objects.get(user=current_user)
        self.addBlankForms(member) # add forms to context
        self.generateTeamInfo(member)
        return render(request, self.template_name, self.context)
    def post(self, request):
        current_user = request.user
        member = Member.objects.get(user=current_user)
        self.addBlankForms(member) # add forms to context
        #process forms
        createTeamForm = CreateTeamForm(request.POST)
        joinTeamForm = JoinTeamForm(request.POST, member=member)
        inviteTeamForm = InviteTeamForm(request.POST)
        leaveTeamForm = LeaveTeamForm(request.POST)
        editBalanceForm = EditBalanceForm(request.POST)
        changeLeaderForm = ChangeLeaderForm(request.POST)
        formCTN = ChangeTeamNameForm(request.POST)
        #Determine which form was submitted
        if 'create_team' in request.POST and createTeamForm.is_valid():
                newTeamObject = Team.objects.create(name=createTeamForm.cleaned_data['name'], charity=createTeamForm.cleaned_data['charity'], leader=member)
                newTeamObject.save()
                addMemberToTeam(member, newTeamObject)
        elif 'join_team' in request.POST and joinTeamForm.is_valid():
                teamName = form.cleaned_data['team']
                try:
                    inviteObject = Invite.objects.get(member=member, team=team)
                    addMemberToTeam(member, Team.objects.get(name=teamName))
                    inviteObject.delete()
                except ObjectDoesNotExist:
                    pass
        elif 'invite_member' in request.POST and inviteTeamForm.is_valid():
                team = inviteTeamForm.cleaned_data['team']
                username = inviteTeamForm.cleaned_data['username']
                try:
                    inviteUser = User.objects.get(username=username)
                    inviteMember = Member.objects.get(user=inviteUser)
                    inviteToTeam = Team.objects.get(name=team)
                    try:
                        inviteObject = Invite.objects.create(team=inviteToTeam, member=inviteMember)
                    except IntegrityError:
                        pass # Member already has an invite to this team
                except ObjectDoesNotExist:
                    pass # Error
        elif 'edit_balance' in request.POST and editBalanceForm.is_valid():
                edit_balance_member = editBalanceForm.cleaned_data['member']
                edit_balance_charity = request.POST['charity'].split('_')[1]
                edit_balance_amount = request.POST['amount']
                EditTeamMemberBalance(editBalanceForm.cleaned_data['member'], request.POST['charity'].split('_')[1], request.POST['amount'])
        elif 'change_leader' in request.POST and changeLeaderForm.is_valid():
                transferLeader(changeLeaderForm.cleaned_data['team'], changeLeaderForm.cleaned_data['NewTeamLeader'])
        elif 'change_team_name' in request.POST and formCTN.is_valid():
                editTeamName(formCTN.cleaned_data['team'], formCTN.cleaned_data['name'])
        elif 'leave_team' in request.POST:
                leaveTeam(leaveTeamForm.cleaned_data['team'], member)
        self.generateTeamInfo(member)
        return render(request, self.template_name, self.context)

class BalancePageView(View):
    template_name = 'sharejarapp/balance.html'
    title = 'Balances'
    context = {}
    def set_context(self, current_user, member):
        self.context['balances'] = getAllBalance(current_user)
        self.context['teambalances'] = getTeamBalance(current_user)
        self.context['directform'] = AddBalanceForm()
        self.context['teamform'] = AddTeamBalanceForm(member=member)
        self.context['title'] = self.title
    def get(self, request):
        current_user = request.user
        member = Member.objects.get(user=current_user)
        self.set_context(current_user, member)
        return render(request, self.template_name, self.context)
    def post(self, request):
        current_user = request.user
        member = Member.objects.get(user=request.user)
        directform = AddBalanceForm(request.POST)
        teamform = AddTeamBalanceForm(request.POST, member=member)
        if directform.is_valid():
            formData = directform.cleaned_data
            addToBalance(member, formData['charity'], formData['increment'])
        if teamform.is_valid():
            formData = teamform.cleaned_data
            addToTeamBalance(member, formData['team'].team, formData['increment'])
        self.set_context(current_user, member)
        return render(request, self.template_name, self.context)

class HomePageView(View):
    login_required = True
    template_name = 'sharejarapp/index.html'
    title = 'ShareJar'
    def get(self, request):
        current_user = request.user
        if Admin.objects.filter(user=current_user).values().exists():
            self.template_name = 'sharejarapp/adminIndex.html'
            self.title = "ShareJar Admin Page"
        context = {'title': self.title}
        return render(request, self.template_name, context)
