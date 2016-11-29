from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.core.exceptions import ObjectDoesNotExist

def getBalance(user):
    member = Member.objects.get(user=user) #get member from current user
    balances = None
    try:
        balances = Balances.objects.all().filter(member=member)
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
