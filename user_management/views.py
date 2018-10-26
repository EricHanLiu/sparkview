from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models.functions import Now
from django.core import serializers
from django.db.models import Q
from django.utils import timezone
import datetime

from .models import Member, Incident, Team, Role, Skill, SkillEntry
from budget.models import Client
from client_area.models import AccountHourRecord, MonthlyReport, Promo
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

    now   = datetime.datetime.now()
    month = now.month
    year  = now.year
    memberHoursThisMonth = AccountHourRecord.objects.filter(member=member, month=month, year=year, is_unpaid=False)

    accounts = member.accounts.filter(Q(status=0) | Q(status=1))

    backupAccounts = Client.objects.filter(Q(cmb=member) | Q(amb=member) | Q(seob=member) | Q(stratb=member)).filter(Q(status=0) | Q(status=1))

    accountHours = {}
    accountAllocation = {}
    for account in accounts:
        hours  = account.getHoursWorkedThisMonthMember(member)
        accountHours[account.id] = hours
        accountAllocation[account.id] = account.getAllocationThisMonthMember(member)

    backupAccountHours = {}
    backupAccountAllocation = {}
    for account in backupAccounts:
        hours  = account.getHoursWorkedThisMonthMember(member)
        backupAccountAllocation[account.id] = 0
        backupAccountHours[account.id] = hours

    scoreBadges = ['secondary', 'danger', 'warning', 'success']

    promos = Promo.objects.filter(account__in=accounts)

    reporting_period = now.day <= 12
    reports = []

    # Reports
    if (reporting_period):
        active_accounts = accounts.filter(status=1)
        for account in active_accounts:
            report, created = MonthlyReport.objects.get_or_create(account=account, month=month, year=year)
            if (created):
                if (account.tier == 1):
                    report.report_type = 2 # Advanced
                else:
                    report.report_type = 1 # Standard
                report.save()
            reports.append(report)


    context = {
        'member'                  : member,
        'hoursThisMonth'          : memberHoursThisMonth,
        'accountHours'            : accountHours,
        'backupHours'             : backupAccountHours,
        'accountAllocation'       : accountAllocation,
        'backupAccountAllocation' : backupAccountAllocation,
        'incidents'               : incidents,
        'memberSkills'            : memberSkills,
        'accounts'                : accounts,
        'backupAccounts'          : backupAccounts,
        'scoreBadges'             : scoreBadges,
        'reporting_period' : reporting_period,
        'reports' : reports,
        'promos' : promos,
        'month_str' : now.strftime("%B")
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
                                  'buffer_seniority_percentage'
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
        teams         = Team.objects.all()
        roles         = Role.objects.all()
        skills        = Skill.objects.all()
        existingUsers = User.objects.filter(member__isnull=True)
        skillOptions  = [0, 1, 2, 3]

        context = {
            'teams'         : teams,
            'roles'         : roles,
            'skills'        : skills,
            'existingUsers' : existingUsers,
            'skillOptions'  : skillOptions
        }

        return render(request, 'user_management/new_member.html', context)
    elif (request.method == 'POST'):

        # Check if we are creating a new user or using an existing one
        useExistingUser = True

        # This should be improved
        if (int(request.POST.get('existing_user')) == 0):
            useExistingUser = False

        if (useExistingUser):
            user_id = request.POST.get('existing_user')
            user    = User.objects.get(id=user_id)
        else:
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
        buffer_total_percentage     = request.POST.get('buffer_total_percentage') #if not request.POST.get('buffer_total_percentage') None else 0
        buffer_learning_percentage  = request.POST.get('buffer_learning_percentage') #if not request.POST.get('buffer_learning_percentage') None else 0
        buffer_trainers_percentage  = request.POST.get('buffer_trainers_percentage') #if not request.POST.get('buffer_trainers_percentage') not None else 0
        buffer_sales_percentage     = request.POST.get('buffer_sales_percentage') #if request.POST.get('buffer_sales_percentage') not None else 0
        buffer_planning_percentage  = request.POST.get('buffer_planning_percentage') #if request.POST.get('buffer_planning_percentage') not None else 0
        buffer_internal_percentage  = request.POST.get('buffer_internal_percentage') #if request.POST.get('buffer_internal_percentage') not None else 0
        buffer_seniority_percentage = request.POST.get('buffer_seniority_percentage')# if request.POST.get('buffer_seniority_percentage') not None else 0

        user.save()

        member = Member.objects.create(
            user=user,
            buffer_total_percentage=buffer_total_percentage,
            buffer_learning_percentage=buffer_learning_percentage,
            buffer_trainers_percentage=buffer_trainers_percentage,
            buffer_sales_percentage=buffer_sales_percentage,
            buffer_planning_percentage=buffer_planning_percentage,
            buffer_internal_percentage=buffer_internal_percentage,
            buffer_seniority_percentage=buffer_seniority_percentage
        )

        # Set role
        member.role = role

        # Set Teams
        member.team.set(teams)
        member.save()

        # Set initial member skills
        skills = Skill.objects.all()

        for skill in skills:
            skillValue = request.POST.get('skill_' + skill.name)
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

        # Update skills
        skills = Skill.objects.all()
        for skill in skills:
            skillScore = request.POST.get('skill_' + skill.name) #if request.POST.get('skill_{{ skill.name }}') not None else 0
            try:
                skillEntry = SkillEntry.objects.get(skill=skill, member=member)
            except SkillEntry.DoesNotExist:
                skillEntry = SkillEntry(skill=skill, member=member)

            skillEntry.score = skillScore
            skillEntry.save()

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
    incidents    = Incident.objects.filter(members=member)
    memberSkills = SkillEntry.objects.filter(member=member)

    now   = datetime.datetime.now()
    month = now.month
    year  = now.year
    memberHoursThisMonth = AccountHourRecord.objects.filter(member=member, month=month, year=year, is_unpaid=False)

    accounts = Client.objects.filter(
                  Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
                  Q(am1=member) | Q(am2=member) | Q(am3=member) |
                  Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
                  Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
              ).filter(Q(status=0) | Q(status=1))

    backupAccounts = Client.objects.filter(Q(cmb=member) | Q(amb=member) | Q(seob=member) | Q(stratb=member)).filter(Q(status=0) | Q(status=1))

    promos = Promo.objects.filter(account__in=accounts)

    accountHours = {}
    accountAllocation = {}
    for account in accounts:
        hours  = account.getHoursWorkedThisMonthMember(member)
        accountHours[account.id] = hours
        accountAllocation[account.id] = account.getAllocationThisMonthMember(member)

    backupAccountHours = {}
    backupAccountAllocation = {}
    for account in backupAccounts:
        hours  = account.getHoursWorkedThisMonthMember(member)
        backupAccountAllocation[account.id] = 0
        backupAccountHours[account.id] = hours

    reporting_period = now.day <= 12
    reports = []

    # Reports
    if (reporting_period):
        active_accounts = accounts.filter(status=1)
        for account in active_accounts:
            report, created = MonthlyReport.objects.get_or_create(account=account, month=month, year=year)
            if (created):
                if (account.tier == 1):
                    report.report_type = 2 # Advanced
                else:
                    report.report_type = 1 # Standard
                report.save()
            reports.append(report)

    scoreBadges = ['secondary', 'danger', 'warning', 'success']

    context = {
        'hoursThisMonth' : memberHoursThisMonth,
        'accountHours'            : accountHours,
        'backupHours'             : backupAccountHours,
        'accountAllocation'       : accountAllocation,
        'backupAccountAllocation' : backupAccountAllocation,
        'member'         : member,
        'memberSkills'   : memberSkills,
        'accounts'       : accounts,
        'backupAccounts' : backupAccounts,
        'scoreBadges'    : scoreBadges,
        'incidents' : incidents,
        'reporting_period' : reporting_period,
        'reports' : reports,
        'promos' : promos,
        'month_str' : now.strftime("%B")
    }

    return render(request, 'user_management/profile.html', context)


@login_required
def training_members(request):
    members      = Member.objects.only('team', 'role')
    memberSkills = SkillEntry.objects.all()

    roleBadges  = ['info', 'primary', 'accent', 'focus']
    scoreBadges = ['secondary', 'danger', 'warning', 'success']

    scoreDescs = ['None', 'Below Average', 'Average', 'Excellent']
    roles      = ['CM', 'AM', 'SEO', 'Strat']

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
