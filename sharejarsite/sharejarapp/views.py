from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("home page")

def teamStats(request):
    return HttpResponse("team page")

def addBalance(request):
    return HttpResponse("add to balance")

def currentBalance(request):
    return HttpResponse("current balance")

def joinTeam(request):
    return HttpResponse("join a team")
