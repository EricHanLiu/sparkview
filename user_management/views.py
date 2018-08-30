from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User

from .models import Member, Incident, Team, Role
from .forms import NewMemberForm, NewTeamForm

@login_required
def index(request):
    return redirect('/user_management/members')

@login_required
def members(request):
    members = Member.objects.all()

    context = {
        'members' : members,
    }

    return render(request, 'user_management/members.html', context)

@login_required
def new_member(request):
    if (request.method == 'GET'):
        teams        = Team.objects.all()
        roles        = Role.objects.all()
        skillOptions = [0, 1, 2, 3]

        context = {
            'teams'        : teams,
            'roles'        : roles,
            'skillOptions' : skillOptions
        }

        return render(request, 'user_management/new_member.html', context)
    elif (request.method == 'POST'):
        # First we make a user, then we make a member
        username        = request.POST.get('username')
        password        = request.POST.get('password')
        hashed_password = make_password(password)
        first_name      = request.POST.get('first_name')
        last_name       = request.POST.get('last_name')
        email           = request.POST.get('email')
        is_staff        = request.POST.get('is_staff')

        # Check if that username is already in use
        is_username_taken = User.objects.filter(username__iexact=username).exists()
        is_email_taken    = User.objects.filter(email__iexact=email).exists()

        if is_username_taken:
            response = {
                'error_message': 'User ' + username + ' already exists.'
            }

            return JsonResponse(response)
        # elif is_email_taken:
        #     response = {
        #         'error_message': 'Email ' + email + ' already exists.'
        #     }
        #
        #     return JsonResponse(response)
        else:
            #user = User.objects.create(username=username, password=hashed_password, first_name=first_name, last_name=last_name, email=email)
            user = User(username=username, password=hashed_password, first_name=first_name, last_name=last_name, email=email)

            if is_staff == 'on':
                user.is_staff = True

        # Now make the member
        team_id = request.POST.get('team')
        print("TEAM ID " + str(team_id))
        team    = Team.objects.get(id=team_id)

        role_id = request.POST.get('role')
        role    = Role.objects.get(id=role_id)

        # Hours
        buffer_total_percentage     = request.POST.get('buffer_total_percentage')
        buffer_learning_percentage  = request.POST.get('buffer_learning_percentage')
        buffer_trainers_percentage  = request.POST.get('buffer_trainers_percentage')
        buffer_sales_percentage     = request.POST.get('buffer_sales_percentage')
        buffer_planning_percentage  = request.POST.get('buffer_planning_percentage')
        buffer_internal_percentage  = request.POST.get('buffer_internal_percentage')
        buffer_seniority_percentage = request.POST.get('buffer_seniority_percentage')
        buffer_buffer_percentage    = request.POST.get('buffer_buffer_percentage')
        buffer_hours_available      = request.POST.get('buffer_hours_available')

        # Member skills
        skill_seo           = request.POST.get('skill_seo')
        skill_cro           = request.POST.get('skill_cro')
        skill_fb            = request.POST.get('skill_fb')
        skill_adwords       = request.POST.get('skill_adwords')
        skill_bing          = request.POST.get('skill_bing')
        skill_linkedin      = request.POST.get('skill_linkedin')
        skill_pinterest     = request.POST.get('skill_pinterest')
        skill_twitter       = request.POST.get('skill_twitter')
        skill_english       = request.POST.get('skill_english')
        skill_french        = request.POST.get('skill_french')
        skill_technical     = request.POST.get('skill_technical')
        skill_confident     = request.POST.get('skill_confident')
        skill_communication = request.POST.get('skill_communication')

        # Last checks
        last_skill_check    = request.POST.get('last_skill_check')
        last_language_check = request.POST.get('last_language_checks')

        user.save()

        member = Member.objects.create(
            user=user,
            team=team,
            buffer_total_percentage=buffer_total_percentage,
            buffer_learning_percentage=buffer_learning_percentage,
            buffer_trainers_percentage=buffer_trainers_percentage,
            buffer_sales_percentage=buffer_sales_percentage,
            buffer_planning_percentage=buffer_planning_percentage,
            buffer_internal_percentage=buffer_internal_percentage,
            buffer_seniority_percentage=buffer_seniority_percentage,
            buffer_buffer_percentage=buffer_buffer_percentage,
            buffer_hours_available=buffer_hours_available,
            skill_seo=skill_seo,
            skill_cro=skill_cro,
            skill_fb=skill_fb,
            skill_adwords=skill_adwords,
            skill_bing=skill_bing,
            skill_linkedin=skill_linkedin,
            skill_pinterest=skill_pinterest,
            skill_twitter=skill_twitter,
            skill_english=skill_english,
            skill_french=skill_french,
            skill_technical=skill_technical,
            skill_confident=skill_confident,
            skill_communication=0, # TODO: Change
            # last_skill_check=last_skill_check,
            # last_language_check=last_language_check
        )

        return JsonResponse({'username' : username})
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
