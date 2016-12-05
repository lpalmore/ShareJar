from django.core.exceptions import ObjectDoesNotExist
from models import Balances, Member, Charity, Team, TeamMemberList, Invite
from django.contrib.auth.models import User
from decimal import *

# Deletes the teamObject instance if it has no remaining members or pending invites
def teamCleanUp(teamObject):
    # Clean up the team if there are no remaining members
    if not TeamMemberList.objects.filter(team=teamObject).exists():
       print "Deleting team" + teamObject.name
       teamObject.delete()

#TODO no longer remove from current team
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
#Allows the user to leave a specific team. Takes user off team list.
#Updates team leader if user is current team leader.
def leaveTeam(teamName, member):
    team = Team.objects.get(name=teamName)

    #remove user from TeamMemberList
    teamMembers = TeamMemberList.objects.get(team=team)
    teamMembers.members.remove(member)

    #if user is leader, update team leader
    if team.leader == member:
        #if they are the only member, delete team
        if teamMembers.members.first() == None:
            print "deleteing team"
            deleteTeam(teamName)
        #otherwise, select random member
        #TODO: they must choose replacement
        else:
            #TODO error
            team.leader = teamMembers.members.first()
            team.save()
    return

#returns True if the user is the leader of a team
def isLeader(member):
    return Team.objects.all().filter(leader=member).first != None

#deletes the team from the database
def deleteTeam(teamName):
    team = Team.objects.get(name=teamName)
    teamMembers = TeamMemberList.objects.get(team=team).delete()
    team.delete()
    #teamMembers = TeamMemberList.objects.get(team=team).delete() #deleting team
    return

#edits the name of the team
def editTeamName(teamName, newTeamName):
    team = Team.objects.all().filter(name=teamName).first()
    team.name = newTeamName
    team.save()
    return

#transfers the leader position to a chosen member of the team
def transferLeader(teamName, newLeaderName):
    team = Team.objects.get(name=teamName)
    newLeaderUser = User.objects.get(username=newLeaderName)
    newLeader = Member.objects.get(user=newLeaderUser)
    #TODO fix error
    team.leader = newLeader
    team.save()
    return

#returns the list of usernames for users on a team
def getUsernamesInTeam(inTeamName):
    team = Team.objects.all().filter(name=inTeamName).first()
    memberlist = TeamMemberList.objects.get(team=team)
    usernames = []
    for member in memberlist.members.all():
        usernames.append(member.user.username)
    return usernames

#gets the balances for each member (for that team) on a team
def getAllTeamBalances(teamName):
    team = Team.objects.get(name=teamName)
    memberlist = TeamMemberList.objects.get(team=team)
    teamMembers = []
    for member in memberlist.members.all():
        teamMembers.append(member)
    balances = None
    try:
        balances = Balances.objects.all().filter(member__in=teamMembers, team=team)
    except ObjectDoesNotExist:
        pass
    return balances

#Allows the team leader to edit the balance of team members
def EditTeamMemberBalance(edit_balance_member, edit_balance_charity, edit_balance_amount):
    user = User.objects.all().filter(username=edit_balance_member).first()
    member = Member.objects.all().filter(user=user)
    charity = Charity.objects.all().filter(charityname = edit_balance_charity).first()
    edit = Balances.objects.all().filter(member = member, charity=charity).first()
    cbalance = edit.balance
    newbalance = cbalance + Decimal(edit_balance_amount)
    if newbalance < 0:
        edit.balance = 0
        edit.save()
        return True
    elif newbalance >=0:
        edit.balance = newbalance
        edit.save()
        return True
    return False

#Gets all the teams a user is on
def GetTeams(teamMember):
    teamName = teamMember.teammemberlist_set.all()
    teams =[]
    for t in teamName:
        teams.append(t.team)
    return teams
