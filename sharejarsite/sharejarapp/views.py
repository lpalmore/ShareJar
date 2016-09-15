from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def home(request):


    template = loader.get_template('sharejarapp/index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def teamStats(request):
    template = loader.get_template('sharejarapp/teamStats.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def addBalance(request):
    template = loader.get_template('sharejarapp/addBalance.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def currentBalance(request):
    template = loader.get_template('sharejarapp/currentBalance.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def joinTeam(request):
    template = loader.get_template('sharejarapp/joinTeam.html')
    context = {
    }
    return HttpResponse(template.render(context, request))
