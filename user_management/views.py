from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models.functions import Now
from django.core import serializers

from .models import Member, Incident, Team, Role, Skill, SkillEntry
from .forms import NewMemberForm, NewTeamForm

@login_required
def index(request):
    return redirect('/user_management/members')


@login_required
def profile(request):
    user         = request.user
    member       = Member.objects.get(user=user)
    incidents    = Incident.objects.filter(members=member)
    memberSkills = SkillEntry.objects.filter(member=member)

    context = {
        'member'       : member,
        'incidents'    : incidents,
        'memberSkills' : memberSkills
    }

    return render(request, 'user_management/profile.html', context)


@login_required
def members(request):
    # Authenticate if staff or not
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')
    members = Member.objects.only('team',
                                  'role',
                                  'buffer_total_percentage',
                                  'buffer_learning_percentage',
                                  'buffer_trainers_percentage',
                                  'buffer_sales_percentage',
                                  'buffer_planning_percentage',
                                  'buffer_internal_percentage',
                                  'buffer_seniority_percentage',
                                  'buffer_buffer_percentage',
                                  'buffer_hours_available'
                                  )

    context = {
        'members' : members,
    }

    return render(request, 'user_management/members.html', context)


@login_required
def new_member(request):
    # Authenticate if staff or not
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')
    if (request.method == 'GET'):
        teams        = Team.objects.all()
        roles        = Role.objects.all()
        skills       = Skill.objects.all()
        skillOptions = [0, 1, 2, 3]

        context = {
            'teams'        : teams,
            'roles'        : roles,
            'skills'       : skills,
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
        elif is_email_taken:
            response = {
                'error_message': 'Email ' + email + ' already exists.'
            }

            return JsonResponse(response)
        else:
            user = User(username=username, password=hashed_password, first_name=first_name, last_name=last_name, email=email)

            if is_staff == 'on':
                user.is_staff = True

        # Now make the member
        # A member can be on many teams
        teams = []
        for team_id in request.POST.getlist('team'):
            teams.append(Team.objects.get(id=team_id))

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
        # skill_seo           = request.POST.get('skill_seo')
        # skill_cro           = request.POST.get('skill_cro')
        # skill_fb            = request.POST.get('skill_fb')
        # skill_adwords       = request.POST.get('skill_adwords')
        # skill_bing          = request.POST.get('skill_bing')
        # skill_linkedin      = request.POST.get('skill_linkedin')
        # skill_pinterest     = request.POST.get('skill_pinterest')
        # skill_twitter       = request.POST.get('skill_twitter')
        # skill_english       = request.POST.get('skill_english')
        # skill_french        = request.POST.get('skill_french')
        # skill_technical     = request.POST.get('skill_technical')
        # skill_confident     = request.POST.get('skill_confident')
        # skill_communication = request.POST.get('skill_communication')

        # Last checks
        last_skill_check    = request.POST.get('last_skill_check')
        last_language_check = request.POST.get('last_language_checks')

        user.save()

        member = Member.objects.create(
            user=user,
            buffer_total_percentage=buffer_total_percentage,
            buffer_learning_percentage=buffer_learning_percentage,
            buffer_trainers_percentage=buffer_trainers_percentage,
            buffer_sales_percentage=buffer_sales_percentage,
            buffer_planning_percentage=buffer_planning_percentage,
            buffer_internal_percentage=buffer_internal_percentage,
            buffer_seniority_percentage=buffer_seniority_percentage,
            buffer_buffer_percentage=buffer_buffer_percentage,
            buffer_hours_available=buffer_hours_available,
            # skill_seo=skill_seo,
            # skill_cro=skill_cro,
            # skill_fb=skill_fb,
            # skill_adwords=skill_adwords,
            # skill_bing=skill_bing,
            # skill_linkedin=skill_linkedin,
            # skill_pinterest=skill_pinterest,
            # skill_twitter=skill_twitter,
            # skill_english=skill_english,
            # skill_french=skill_french,
            # skill_technical=skill_technical,
            # skill_confident=skill_confident,
            # skill_communication=skill_communication,
            last_skill_check=Now(),
            last_language_check=Now()
        )

        # Set Teams
        member.team.set(teams)
        member.save()

        # Set initial member skills
        skills = Skill.objects.all()

        for skill in skills:
            skillValue = request.POST.get(skill.name)
            if skillValue == None:
                skillValue = 0

            SkillEntry.objects.create(skill=skill, member=member, score=skillValue)

        return redirect('/user_management/members')
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def edit_member(request, id):
    # Authenticate if staff or not
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    if (request.method == 'POST'):

        # Member to update
        member = get_object_or_404(Member, id=id)

        # User parameters
        first_name      = request.POST.get('first_name')
        last_name       = request.POST.get('last_name')
        email           = request.POST.get('email')
        is_staff        = (request.POST.get('is_staff') == 'on')

        # Member parameters
        # Now make the member
        # A member can be on many teams
        teams = []
        for team_id in request.POST.getlist('team'):
            teams.append(Team.objects.get(id=team_id))

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


        # Check if we are updating non-language skills
        if (member.skill_seo           != skill_seo or
            member.skill_cro           != skill_cro or
            member.skill_fb            != skill_fb  or
            member.skill_adwords       != skill_adwords or
            member.skill_bing          != skill_bing or
            member.skill_linkedin      != skill_linkedin or
            member.skill_pinterest     != skill_pinterest or
            member.skill_twitter       != skill_twitter or
            member.skill_technical     != skill_technical or
            member.skill_confident     != skill_confident or
            member.skill_communication != skill_communication):

            member.last_skill_check = Now()

        # Check if we are updating language skills
        if (member.skill_english != skill_english or
            member.skill_french  != skill_french):

            member.last_language_check = Now()

        # Set all of the member skills with the edited variables
        # User parameters
        member.user.first_name = first_name
        member.user.last_name  = last_name
        member.user.email      = email
        member.user.is_staff   = is_staff

        # Member parameters
        member.team.set(teams)
        member.role = role

        # Hours
        member.buffer_total_percentage     = buffer_total_percentage
        member.buffer_learning_percentage  = buffer_learning_percentage
        member.buffer_trainers_percentage  = buffer_trainers_percentage
        member.buffer_sales_percentage     = buffer_sales_percentage
        member.buffer_planning_percentage  = buffer_planning_percentage
        member.buffer_internal_percentage  = buffer_internal_percentage
        member.buffer_seniority_percentage = buffer_seniority_percentage
        member.buffer_buffer_percentage    = buffer_buffer_percentage
        member.buffer_hours_available      = buffer_hours_available

        # Member skills
        member.skill_seo           = skill_seo
        member.skill_cro           = skill_cro
        member.skill_fb            = skill_fb
        member.skill_adwords       = skill_adwords
        member.skill_bing          = skill_bing
        member.skill_linkedin      = skill_linkedin
        member.skill_pinterest     = skill_pinterest
        member.skill_twitter       = skill_twitter
        member.skill_english       = skill_english
        member.skill_french        = skill_french
        member.skill_technical     = skill_technical
        member.skill_confident     = skill_confident
        member.skill_communication = skill_communication

        member.user.save()
        member.save()

        return redirect('/user_management/members')
    else:
        member       = Member.objects.get(id=id)
        teams        = Team.objects.all()
        roles        = Role.objects.all()
        memberSkills = SkillEntry.objects.filter(member=member)
        skillOptions = [0, 1, 2, 3]

        context = {
            'member'       : member,
            'teams'        : teams,
            'roles'        : roles,
            'memberSkills' : memberSkills,
            'skillOptions' : skillOptions
        }

        return render(request, 'user_management/edit_member.html', context)


@login_required
def teams(request):
    teams = Team.objects.all()

    context = {
        'teams' : teams,
    }

    return render(request, 'user_management/teams.html', context)


@login_required
def new_team(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')
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


@login_required
def members_single(request, id):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    member = Member.objects.get(id=id)
    memberSkills = SkillEntry.objects.filter(member=member)

    context = {
        'member'       : member,
        'memberSkills' : memberSkills
    }

    return render(request, 'user_management/profile.html', context)


@login_required
def training_members(request):
    members      = Member.objects.only('team', 'role')
    memberSkills = SkillEntry.objects.all()

    scoreBadges = ['danger', 'brand', 'info', 'success']

    scoreDescs = ['None', 'Below Average', 'Average', 'Excellent']

    context = {
        'members'     : members,
        'memberSkills': memberSkills,
        'scoreBadges' : scoreBadges,
        'scoreDescs'  : scoreDescs
    }

    return render(request, 'user_management/training.html', context)


@login_required
def training_members_json(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    members = list(Member.objects.values())
    return JsonResponse(members, safe=False)


@login_required
def skills(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    skills = Skill.objects.all()

    context = {
        'skills' : skills
    }

    return render(request, 'user_management/skills.html', context)


@login_required
def skills_single(request, id):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    skill = Skill.objects.get(id=id)

    context = {
        'skill' : skill
    }

    return render(request, 'user_management/skills_single.html', context)


@login_required
def skills_new(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    if (request.method == 'POST'):
        skill_name = request.POST.get('skillname')
        newSkill = Skill.objects.create(name=skill_name)

        # Assign a default value to every member
        members = Member.objects.all()
        for member in members:
            SkillEntry.objects.create(skill=newSkill, member=member, score=0)

        return redirect('/user_management/skills')
    else:
        return HttpResponse('Invalid request type')
