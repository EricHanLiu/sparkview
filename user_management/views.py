from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import Member, Incident, Team

@login_required
def index():
    return redirect(members)

@login_required
def members(request):
    members = Member.objects.all()

    context = {
        'members' : members,
    }

    return render(request, 'user_management/members.html', context)

@login_required
def new_member(request):
    if (request.method == 'POST'):
        pass
    else:
        return HttpResponse('You are at the wrong place')

@login_required
def edit_member(request):
    if (request.method == 'POST'):
        pass
    else:
        return HttpResponse('You are at the wrong place')

@login_required
def teams(request):
    teams = Team.objects.all()

    context = {
        'teams' : teams,
    }

    return render(request, 'user_management/teams.html', context)

@login_required
def new_team(request):
    if (request.method == 'POST'):
        # Information about the team
        teamname = request.POST.get('teamname')

        # Create the team
        team = Team.objects.create(name=teamname)

        context = {}
        return JsonResponse(context)
    else:
        return HttpResponse('You are at the wrong place')

@login_required
def edit_team(request):
    if (request.method == 'POST'):
        pass
    else:
        return HttpResponse('You are at the wrong place')
