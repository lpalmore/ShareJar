from django.core.exceptions import ObjectDoesNotExist
from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.contrib.auth.models import User

# Deletes the teamObject instance if it has no remaining members or pending invites
def teamCleanUp(teamObject):
    # Clean up the team if there are no remaining members
    if not TeamMemberList.objects.filter(team=teamObject).exists():
       print "Deleting team" + teamObject.name
       teamObject.delete()

#TODO no longer remove from current team
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

'''
    teamName: String
    member: member id of user
'''
def leaveTeam(teamName, member):
    team = Team.objects.all().filter(name=teamName).first()

    #remove user from TeamMemberList
    teamMembers = TeamMemberList.objects.all().filter(team=team, member=member).all().delete()

    #if user is leader, update team leader
    if team.leader == member:
        #if they are the only member, delete team
        if not TeamMemberList.objects.all().filter(team=team).all().exists():
            print "deleteing team"
            deleteTeam(teamName)
        #otherwise, select random member
        #TODO: they must choose replacement
        else:
            #TODO error
            team.leader = TeamMemberList.objects.all().filter(team=team).first()
            team.save()
    return

def isLeader(member):
    return Team.objects.all().filter(leader=member).first != None

def deleteTeam(teamName):
    team = Team.objects.all().filter(name=teamName).first().delete() #deleting team
    return

def editTeamName(teamName, newTeamName):
    team = Team.objects.all().filter(name=teamName).first()
    team.name = newTeamName
    team.save()
    return

def transferLeader(teamName, newLeaderName):
    team = Team.objects.all().filter(name=teamName).first()
    newLeaderUser = User.objects.all().filter(username=newLeaderName).first()
    newLeader = Member.objects.all().filter(user=newLeaderUser).first()
    #TODO fix error
    team.leader = newLeader
    team.save()
    return

def getUsernamesInTeam(inTeamName):
    team = Team.objects.all().filter(name=inTeamName).first()
    memberlist = TeamMemberList.objects.all().filter(team = team).all()
    usernames = []
    for member in memberlist:
        usernames.append(member.member.user.username)
    return usernames

def getAllTeamBalances(teamName):
    team = Team.objects.all().filter(name=teamName).first()
    memberlist = TeamMemberList.objects.all().filter(team = team).all()
    teamMembers = []
    for tml in memberlist:
        teamMembers.append(tml.member)
    balances = None
    try:
        balances = Balances.objects.all().filter(member__in=teamMembers)
    except ObjectDoesNotExist:
        pass
    return balances

def EditTeamMemberBalance(edit_balance_member, edit_balance_charity, edit_balance_amount):
    edit = Balances.objects.all().filter(member = edit_balance_member, charity=edit_balance_charity)
    cbalance = edit.balance
    newbalance = cbalance+edit_balance_amount
    if newbalance < 0:
        return False
    elif newbalance >=0:
        edit.balance = newbalance
        edit.save()
        return True
    return False

def GetTeams(teamMember):
    teamName = TeamMemberList.objects.all().filter(member=teamMember)
    teams =[]
    for t in teamName:
        teams.append(t.team)
    return teams
