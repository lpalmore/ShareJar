from django.core.exceptions import ObjectDoesNotExist
from models import Balances, Member, Charity, Team, TeamMemberList, Invite


# Deletes the teamObject instance if it has no remaining members or pending invites
def teamCleanUp(teamObject):
    # Clean up the team if there are no remaining members
    if not TeamMemberList.objects.filter(team=teamObject).exists():
       print "Deleting team" + teamObject.name
       teamObject.delete()


#Adds member to specified team. Removes member from current team if there is one
def addMemberToTeam(member, team=None):
    if not member:
        return
    try:
        #Change team list entry for this member to the new team
        teamList = TeamMemberList.objects.get(team=team)
        teamList.members.add(member)
        teamList.save()
    except ObjectDoesNotExist:
        #Add member to new team
        teamList = TeamMemberList.objects.create(team=team)
        teamList.members.add(member)
        teamList.save()
'''
    teamName: String
    member: member id of user
'''
def leaveTeam(teamName, member):
    team = Team.objects.all().filter(name=teamName).first()

    #remove user from TeamMemberList
    teamMembers = TeamMemberList.objects.all().filter(team=team).first()
    teamMembers.members.remove(member)

    #if user is leader, update team leader
    if team.leader == member:
        #if they are the only member, delete team
        if teamMembers.members == None:
            print "deleteing team"
            deleteTeam(teamName)
        #otherwise, select random member
        #TODO: they must choose replacement
        else:
            team.leader = TeamMemberList.objects.all().filter(team=team).first()
            team.save()
    return

def deleteTeam(teamName):
    team = Team.objects.all().filter(name=teamName).first().delete()
    teamMembers = TeamMemberList.objects.all().filter(team=team).delete() #deleting team
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

def getMembers(teamName):
    team = Team.objects.all().filter(name=teamName).first()
    members = TeamMemberList.objects.all().filter(team = team).members
    return
