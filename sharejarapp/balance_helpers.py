from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.core.exceptions import ObjectDoesNotExist

def getAllBalance(user):
    member = Member.objects.get(user=user) #get member from current user
    balances = None
    try:
        balances = Balances.objects.all().filter(member=member)
    except ObjectDoesNotExist:
        pass
    return balances

def getTeamBalance(user):
    member = Member.objects.get(user=user) #get member from current user
    teamMemberList = member.teammemberlist_set.all()
    balances = None
    if not teamMemberList == None:
        for teamList in teamMemberList:
            team = teamList.team
            try:
                balance = Balances.objects.all().filter(member=member, team=team)
                if balances == None:
                    balances = balance
                else:
                    balances.append(balance)
            except ObjectDoesNotExist:
                pass
    return balances

def addToBalance(member, charityname, increment):
    success = False
    if increment >= 0:
        try:
            b = Balances.objects.get(member=member, charity=charityname)
            b.balance += increment
            b.save()
        except ObjectDoesNotExist:
            b = Balances.objects.create(member=member, charity=charityname, balance=increment)
        success = True
    return success

def addToTeamBalance(member, team, increment):
    success = False
    if increment >= 0:
        try:
            b = Balances.objects.get(member=member, team=team)
            b.balance += increment
            b.save()
        except ObjectDoesNotExist:
            b = Balances.objects.create(member=member, team=team, balance=increment)
        success = True
    return success