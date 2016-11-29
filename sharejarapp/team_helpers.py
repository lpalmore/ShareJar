from django.core.exceptions import ObjectDoesNotExist
from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.utils.crypto import get_random_string


# Deletes the teamObject instance if it has no remaining members or pending invites
def teamCleanUp(teamObject):
    # Clean up the team if there are no remaining members
    if not TeamMemberList.objects.filter(team=teamObject).exists():
       print "Deleting team" + teamObject.name
       teamObject.delete()


#Adds member to specified team. Removes member from current team if there is one
def addMemberToTeam(member, newTeamObject, currentTeamObject=None):
    if not member:
        return
    if currentTeamObject:
        #Change team list entry for this member to the new team
        listObject = TeamMemberList.objects.get(member=member, team=currentTeamObject)
        listObject.team = newTeamObject;
        listObject.save()
        teamCleanUp(currentTeamObject)
    else:
        #Add member to new team
        listObject = TeamMemberList.objects.create(member=member, team=newTeamObject)
        listObject.save()
