from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from forms import UserForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect


def createUser(request):
    #if post request, create the new user
    if request.method == "POST":
        form = UserForm(request.POST)
        print form.is_valid()
        if form.is_valid():
            user = form.cleaned_data['username']
            print user;
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            newUser = User.objects.create_user(user, email, password)
            return HttpResponseRedirect('login')
    else:
        form = UserForm()
    template = loader.get_template('registration/createUser.html')
    context = {
        'form': form,
    }
    return HttpResponse(template.render(context, request))

@login_required
def home(request):
    template = loader.get_template('sharejarapp/index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def teamStats(request):
    template = loader.get_template('sharejarapp/teamStats.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def addBalance(request):
    template = loader.get_template('sharejarapp/addBalance.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def currentBalance(request):
    template = loader.get_template('sharejarapp/currentBalance.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

@login_required
def joinTeam(request):
    template = loader.get_template('sharejarapp/joinTeam.html')
    context = {
    }
    return HttpResponse(template.render(context, request))
