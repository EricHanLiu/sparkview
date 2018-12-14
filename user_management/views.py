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
import datetime, calendar

from .models import Member, Incident, Team, Role, Skill, SkillEntry, BackupPeriod, Backup, TrainingHoursRecord
from budget.models import Client
from client_area.models import AccountHourRecord, MonthlyReport, Promo
from .forms import NewMemberForm, NewTeamForm

@login_required
def index(request):
    return redirect('/user_management/members')

@login_required
def members(request):
    # Authenticate if staff or not
    if not request.user.is_staff:
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
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')
    if (request.method == 'GET'):
        teams = Team.objects.all()
        roles = Role.objects.all()
        skills = Skill.objects.all()
        existingUsers = User.objects.filter(member__isnull=True)
        skillOptions = [0, 1, 2, 3]

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
        buffer_seniority_percentage = request.POST.get('buffer_seniority_percentage') # if request.POST.get('buffer_seniority_percentage') not None else 0

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
    if not request.user.is_staff:
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
    if not request.user.is_staff:
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
def members_single(request, id=0):
    if not request.user.is_staff and id != 0:
        return HttpResponse('You do not have permission to view this page')

    if id == 0: # This is a profile page
        member = Member.objects.get(user=request.user)
    else:
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
              ).filter(Q(status=0) | Q(status=1)).order_by('client_name')

    backup_periods = BackupPeriod.objects.filter(start_date__lte=now, end_date__gte=now)
    backups = Backup.objects.filter(member=member, period__in=backup_periods, approved=True)

    backing_me = backup_periods.filter(member=member)

    starAccounts = Client.objects.none()
    if request.user.is_staff:
        starAccounts = Client.objects.filter(star_flag=True)

    promos = Promo.objects.filter(account__in=accounts)

    value_added_hours = AccountHourRecord.objects.filter(member=member, month=month, year=year, is_unpaid=True)

    # for row in value_added_hours:
    #     row['account'] = Client.objects.get(id=row['account'])

    accountHours = {}
    accountAllocation = {}
    for account in accounts:
        hours  = account.getHoursWorkedThisMonthMember(member)
        va_hours = account.value_added_hours_month_member(member)
        accountHours[account.id] = hours
        accountAllocation[account.id] = account.getAllocationThisMonthMember(member)

    backupAccountHours = {}
    backupAccountAllocation = {}

    starAccountHours = {}
    starAccountAllocation = {}

    reporting_period = now.day <= 31
    reports = []

    """
    Trainer and trainee hours
    """
    trainer_hours_this_month = TrainingHoursRecord.objects.filter(trainer=member, month=now.month, year=now.year)
    trainee_hours_this_month = TrainingHoursRecord.objects.filter(trainee=member, month=now.month, year=now.year)

    trainee_hour_total = 0.0
    for trainee_hour in trainee_hours_this_month:
        trainee_hour_total += trainee_hour.hours

    # Reports
    if reporting_period:
        active_accounts = accounts.filter(status=1)
        last_month = month - 1
        if last_month == 0:
            last_month = 12
        for account in active_accounts:
            report, created = MonthlyReport.objects.get_or_create(account=account, month=last_month, year=year)
            if created:
                if account.tier == 1:
                    report.report_type = 2 # Advanced
                else:
                    report.report_type = 1 # Standard
                report.save()
            reports.append(report)

    scoreBadges = ['secondary', 'danger', 'warning', 'success']

    context = {
        'hoursThisMonth' : memberHoursThisMonth,
        'accountHours' : accountHours,
        'backupHours' : backupAccountHours,
        'accountAllocation' : accountAllocation,
        'backupAccountAllocation' : backupAccountAllocation,
        'member' : member,
        'memberSkills' : memberSkills,
        'accounts' : accounts,
        'backups' : backups,
        'trainer_hours_this_month': trainer_hours_this_month,
        'trainee_hours_this_month': trainee_hours_this_month,
        'trainee_hour_total': trainee_hour_total,
        'backing_me' : backing_me,
        'scoreBadges' : scoreBadges,
        'incidents' : incidents,
        'reporting_period' : reporting_period,
        'reports' : reports,
        'promos' : promos,
        'value_added_hours' : value_added_hours,
        'month_str' : now.strftime("%B"),
        'last_month_str' : calendar.month_name[last_month],
        'starAccounts' : starAccounts,
        'starAccountHours' : starAccountHours,
        'starAccountAllocation' : starAccountAllocation
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
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    members = list(Member.objects.values())
    return JsonResponse(members, safe=False)


@login_required
def skills(request):
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    skills = Skill.objects.all()

    context = {
        'skills' : skills
    }

    return render(request, 'user_management/skills.html', context)


@login_required
def skills_single(request, id):
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    skill = Skill.objects.get(id=id)

    context = {
        'skill' : skill
    }

    return render(request, 'user_management/skills_single.html', context)


@login_required
def skills_new(request):
    if not request.user.is_staff:
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


@login_required
def backups(request):
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    if request.method == 'POST':
        """
        Creates a backup period
        """
        form_type = request.POST.get('type')
        if form_type == 'period':
            member_id = request.POST.get('member')
            member = Member.objects.get(id=member_id)

            start_date = datetime.datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')

            bp = BackupPeriod()
            bp.member = member
            bp.start_date = start_date
            bp.end_date = end_date
            bp.save()
        elif form_type == 'backup':
            member_id = request.POST.get('member')
            member = Member.objects.get(id=member_id)
            account_id = request.POST.get('account')
            account = Client.objects.get(id=account_id)
            bp_id = request.POST.get('period')
            bp = BackupPeriod.objects.get(id=bp_id)
            bc_link = request.POST.get('bc_link')

            b = Backup()
            b.account = account
            b.member = member
            b.period = bp
            b.bc_link = bc_link
            b.save()
        elif form_type == 'approval':
            bu_id = request.POST.get('bu_id')

            approved_by = Member.objects.get(user=request.user)

            b = Backup.objects.get(id=bu_id)
            b.approved = True
            b.approved_by = approved_by
            b.save()
        elif form_type == 'delete':
            bu_id = request.POST.get('bu_id')
            Backup.objects.get(id=bu_id).delete()
        elif form_type == 'edit':
            bu_id = request.POST.get('edit-bu-id')
            bu_member_id = request.POST.get('member')
            bu_account_id = request.POST.get('account')
            bu_bc_link = request.POST.get('bc_link')
            bu = Backup.objects.get(id=bu_id)
            member = Member.objects.get(id=bu_member_id)
            account = Client.objects.get(id=bu_account_id)

            bu.member = member
            bu.account = account
            bu.bc_link = bu_bc_link

            bu.save()

        return redirect('/user_management/backups')

    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(7)
    seven_days_future = now + datetime.timedelta(7)
    members = Member.objects.all()
    accounts = Client.objects.filter(status=1)

    #backup_periods = BackupPeriod.objects.filter(start_date__gte=seven_days_ago, end_date__lte=seven_days_future)
    backup_periods = BackupPeriod.objects.all()
    active_backups = backup_periods.filter(start_date__lte=now, end_date__gte=now)
    non_active_backup_periods = backup_periods.exclude(start_date__lte=now, end_date__gte=now)

    context = {
        'members' : members,
        'accounts' : accounts,
        'active_backups' : active_backups,
        'non_active_backup_periods': non_active_backup_periods
    }

    return render(request, 'user_management/backup.html', context)


@login_required
def add_training_hours(request):
    """
    Adds a training hour record
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    #trainer_id = request.POST.get('trainer_id')
    trainer = Member.objects.get(user=request.user)

    trainee_id = request.POST.get('trainee_id')
    trainee = Member.objects.get(id=trainee_id)

    if trainer == trainee:
        return HttpResponse('You can\'t train yourself!')

    month = request.POST.get('month')
    year = request.POST.get('year')
    hours = request.POST.get('hours')

    TrainingHoursRecord.objects.create(trainee=trainee, trainer=trainer, month=month, year=year, hours=hours)

    return redirect('/clients/accounts/report_hours')
