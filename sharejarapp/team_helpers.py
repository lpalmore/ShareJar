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

'''
    teamName: String
    member: member id of user
'''
def leaveTeam(teamName, member):
    team = Team.objects.all().filter(name=teamName)

    #remove user from TeamMemberList
    teamMembers = TeamMemberList.objects.all().filter(team=team, member=member).all().delete()

    #if user is leader, update team leader
    if team.leader == member:
        #if they are the only member, delete team
        if not TeamMemberList.objects.all().filter(team=team).all().exists():
            deleteTeam(teamName)
        #otherwise, select random member
        #TODO: they must choose replacement
        else:
            team.leader = TeamMemberList.objects.all().filter(team=team).first()
            team.save()
    return

def deleteTeam(teamName):
    team = Team.objects.all().filter(name=teamName).first().delete() #deleting team
    return

def editTeamName(teamName, newTeamName):
    team = Team.objects.all().filter(name=teamName).first()
    team.name = newTeamName
    team.save()
    return

def transferLeader(teamName, newLeader):
    team = Team.objects.all().filter(name=teamName).first()
    team.leader = newLeader
    team.save()
    return
