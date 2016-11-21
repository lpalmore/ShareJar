from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.utils.crypto import get_random_string

#Adds member to specified team. Removes member from current team if there is one
def addMemberToTeam(member, newTeamObject, currentTeamObject=None):
    if not member:
        return
    if currentTeamObject:
        #Change team list entry for this member to the new team
        listObject = TeamMemberList.objects.get(member=member, team=currentTeamObject)
        listObject.team = newTeamObject;
        listObject.save()
    else:
        #Add member to new team
        listObject = TeamMemberList.objects.create(member=member, team=newTeamObject)
        listObject.save()

def generateCode():
    obs = Invite.objects.all()
    existingCodes = [ob.code for ob in obs]
    code = get_random_string(length=6)
    while code in existingCodes:
        code = get_random_string(lengt=6)
    return code
