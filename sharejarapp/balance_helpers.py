from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.core.exceptions import ObjectDoesNotExist

#Gets every balance associated with the user
def getAllBalance(user):
    member = Member.objects.get(user=user) #get member from current user
    balances = None
    try:
        balances = Balances.objects.all().filter(member=member, team=None)
    except ObjectDoesNotExist:
        pass
    return balances

#Gets the balances of a user for specific team
def getTeamBalance(user):
    member = Member.objects.get(user=user) #get member from current user
    teamMemberList = member.teammemberlist_set.all()
    balances = []
    if not teamMemberList == None:
        for teamList in teamMemberList:
            team = teamList.team
            try:
                balance = Balances.objects.get(member=member, team=team)
                balances.append(balance)
            except ObjectDoesNotExist:
                pass
    return balances

#Updates the balance for a user by charity according to the entered value 
def addToBalance(member, charityname, increment):
    success = False
    if increment >= 0:
        try:
            b = Balances.objects.get(member=member, charity=charityname, team=None)
            b.balance += increment
            b.save()
        except ObjectDoesNotExist:
            b = Balances.objects.create(member=member, charity=charityname, team=None,balance=increment)
        success = True
    return success

#Updates the balance for a user by team according to the entered value
def addToTeamBalance(member, team, increment):
    success = False
    if increment >= 0:
        try:
            b = Balances.objects.get(member=member, team=team, charity=team.charity)
            b.balance += increment
            b.save()
        except ObjectDoesNotExist:
            b = Balances.objects.create(member=member, team=team, charity=team.charity, balance=increment)
        success = True
    return success
