from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, Http404
from django.contrib.auth.models import User
from django.db.models import Sum, Q
import datetime
import calendar

from .models import Member, Incident, Team, Role, Skill, SkillEntry, BackupPeriod, Backup, TrainingHoursRecord, \
    HighFive, TrainingGroup, SkillHistory, SkillCategory
from budget.models import Client
from client_area.models import AccountHourRecord, MonthlyReport, Promo, PhaseTaskAssignment, MandateHourRecord, \
    Mandate, OnboardingStep
from notifications.models import Todo


@login_required
def index(request):
    return redirect('/user_management/members')


@login_required
def members(request):
    # Authenticate if staff or not
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'POST':
        members_resp = {}
        count = 0

        members = Member.objects.filter(deactivated=False).order_by('user__first_name')
        for member in members:
            members_resp[count]['id'] = member.id
            members_resp[count]['name'] = member.user.get_full_name()
            count += 1

        return JsonResponse(members_resp)

    members = Member.objects.only('team',
                                  'role',
                                  'buffer_total_percentage',
                                  'buffer_learning_percentage',
                                  'buffer_trainers_percentage',
                                  'buffer_sales_percentage',
                                  'buffer_planning_percentage',
                                  'buffer_internal_percentage',
                                  'buffer_seniority_percentage'
                                  ).filter(deactivated=False).order_by('user__first_name')

    total_hours_available = 0.0
    total_actual_hours = 0.0
    total_value_added_hours = 0.0
    total_active_accounts = 0.0
    total_onboarding_accounts = 0.0

    for member in members:
        # TODO: Make sure all of these calls are cached
        total_hours_available += member.hours_available
        total_actual_hours += member.actual_hours_month()
        total_value_added_hours += member.value_added_hours_this_month
        total_active_accounts += member.active_accounts_count
        total_onboarding_accounts += member.onboarding_accounts_count

    context = {
        'members': members,
        'total_hours_available': round(total_hours_available, 2),
        'total_actual_hours': round(total_actual_hours, 2),
        'total_value_added_hours': round(total_value_added_hours, 2),
        'total_active_accounts': round(total_active_accounts, 2),
        'total_onboarding_accounts': round(total_onboarding_accounts, 2)
    }

    return render(request, 'user_management/members.html', context)


@login_required
def member_dashboard(request, id):
    # Authenticate if staff or not
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    # HOURS REPORT INFO
    # Get account related metrics
    member = get_object_or_404(Member, id=id)

    # Members, Teams, Roles
    members = Member.objects.filter(deactivated=False).order_by('user__first_name')
    teams = Team.objects.all()
    roles = Role.objects.all()

    # If filter request was made, then narrow the member/teams objects
    teams_request = request.GET.getlist('filter-team')
    roles_request = request.GET.getlist('filter-role')

    now = datetime.datetime.now()
    years = [i for i in range(2018, now.year + 1)]

    q_month = request.GET.get('month')
    q_year = request.GET.get('year')

    month = int(q_month) if q_month else now.month
    year = int(q_year) if q_year else now.year

    # The following variable will be used to control what is shown in the dashboard
    # Reason for this is that not everything is available historically
    load_everything = month == now.month and year == now.year

    selected = {
        'month': month,
        'year': year
    }

    # Convert to role objects
    filtered_roles = None
    filtered_teams = None
    if teams_request:
        filtered_teams = teams.filter(id__in=teams_request)
        members = members.filter(team__in=filtered_teams)
    if roles_request:
        filtered_roles = roles.filter(id__in=roles_request)
        members = members.filter(role__in=filtered_roles)

    # get accounts of filtered members
    accounts = Client.objects.filter(
        Q(cm1__in=members) | Q(cm2__in=members) | Q(cm3__in=members) | Q(am1__in=members) | Q(am2__in=members) | Q(
            am3__in=members) | Q(seo1__in=members) | Q(seo2__in=members) | Q(seo3__in=members) | Q(
            strat1__in=members) | Q(
            strat2__in=members) | Q(strat3__in=members)).order_by('client_name')

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0
    training_aggregate = 0.0

    for memb in members:
        memb.actual_hours_tmp = memb.actual_hours_other_month(month, year)
        actual_aggregate += memb.actual_hours_tmp
        memb.allocated_hours_tmp = memb.allocated_hours_other_month(month, year)
        allocated_aggregate += memb.allocated_hours_tmp
        memb.available_hours_tmp = memb.hours_available_other_month(month, year)
        available_aggregate += memb.available_hours_tmp
        memb.training_hours_tmp = memb.training_hours_other_month(month, year)
        training_aggregate += memb.training_hours_tmp

    if allocated_aggregate + available_aggregate == 0:
        capacity_rate = 0
    else:
        capacity_rate = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

    if allocated_aggregate == 0:
        utilization_rate = 0
    else:
        utilization_rate = 100 * (actual_aggregate / allocated_aggregate)

    # Total management fee
    # total_management_fee = 0.0
    total_allocated_hours = 0.0

    for acc in accounts:
        # total_management_fee += aa.total_fee
        total_allocated_hours += acc.all_hours

    # hours worked this month
    # now = datetime.datetime.now()
    # month = now.month
    # year = now.year
    total_hours_worked = \
        AccountHourRecord.objects.filter(month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
    if total_hours_worked is None:
        total_hours_worked = 0.0

    try:
        allocation_ratio = total_hours_worked / total_allocated_hours
    except ZeroDivisionError:
        allocation_ratio = 0.0

    # PROMO INFO
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(1)
    today_start = datetime.datetime.combine(today, datetime.time())
    today_end = datetime.datetime.combine(tomorrow, datetime.time())
    this_month = datetime.datetime(today.year, today.month, 1)
    next_month = datetime.datetime(today.year, today.month + 1 if today.month != 12 else 1, 1)

    promos_start_today = Promo.objects.filter(start_date__gte=today_start,
                                              start_date__lt=today_end) if load_everything else None
    promos_end_today = Promo.objects.filter(end_date__gte=today_start,
                                            end_date__lt=today_end) if load_everything else None

    # ONBOARDING ACCOUNTS INFO
    onboarding_accounts = accounts.filter(status=0)
    num_onboarding = onboarding_accounts.count()

    # TODO: This will be rethought for Eric's ticket
    avg_onboarding_days = 0
    for acc in onboarding_accounts:
        avg_onboarding_days += acc.onboarding_duration_elapsed
    if num_onboarding != 0:
        avg_onboarding_days /= num_onboarding

    late_accounts = len([account for account in onboarding_accounts if account.is_late_to_onboard])
    late_percentage = 0.0
    if num_onboarding != 0:
        late_percentage = 100.0 * late_accounts / num_onboarding

    # BUDGETS INFO
    # Monthly budget updates
    active_accounts = accounts.filter(salesprofile__ppc_status=1) if load_everything else None
    budget_updated_accounts = active_accounts.filter(budget_updated=True) if load_everything else None
    budget_not_updated_accounts = active_accounts.filter(budget_updated=False) if load_everything else None
    budget_updated_percentage = 0.0
    if load_everything and active_accounts.count() != 0:
        budget_updated_percentage = 100.0 * budget_updated_accounts.count() / active_accounts.count()

    # Overspend projection - get top 5 overspending and underspending accounts
    overspend_accounts = sorted(filter(lambda a: a.projected_loss < 0, active_accounts),
                                key=lambda a: a.projected_refund, reverse=True) if load_everything else None
    underspend_accounts = sorted(filter(lambda a: a.projected_loss > 0, active_accounts),
                                 key=lambda a: a.projected_loss, reverse=True) if load_everything else None
    top_five_overspend = overspend_accounts[0:5] if load_everything else None
    top_five_underspend = underspend_accounts[0:5] if load_everything else None
    num_overspend = len(overspend_accounts) if load_everything else None
    num_underspend = len(underspend_accounts) if load_everything else None

    total_projected_loss = 0.0
    total_projected_overspend = 0.0
    if load_everything:
        for account in overspend_accounts:
            total_projected_overspend += account.project_yesterday - account.current_budget
        for account in underspend_accounts:
            total_projected_loss += account.projected_loss

    # 90 DAYS NOTIFICATIONS INFO
    onboard_active_accounts = accounts.filter(Q(status=0) | Q(status=1))
    num_outstanding_90_days = PhaseTaskAssignment.objects.filter(complete=False,
                                                                 account__in=onboard_active_accounts).count() if load_everything else None

    # FLAGGED ACCOUNTS INFO
    flagged_accounts = accounts.filter(star_flag=True) if load_everything else None

    context = {
        'member': member,
        'capacity_rate': capacity_rate,
        'utilization_rate': utilization_rate,
        'allocation_ratio': allocation_ratio,
        'total_allocated_hours': total_allocated_hours,
        'total_hours_worked': total_hours_worked,
        'actual_aggregate': actual_aggregate,
        'allocated_aggregate': allocated_aggregate,
        'available_aggregate': available_aggregate,
        'total_hours_trained': training_aggregate,
        'filtered_teams': filtered_teams,
        'filtered_roles': filtered_roles,
        'promos_start_today': promos_start_today,
        'promos_end_today': promos_end_today,
        'onboarding_accounts': onboarding_accounts,
        'num_onboarding': num_onboarding,
        'average_onboarding_days': avg_onboarding_days,
        'onboarding_late_percentage': late_percentage,
        'budget_not_updated_accounts': budget_not_updated_accounts,
        'budget_updated_percentage': budget_updated_percentage,
        'top_five_overspend': top_five_overspend,
        'num_overspend': num_overspend,
        'total_overspend_risk': total_projected_overspend,
        'top_five_underspend': top_five_underspend,
        'num_underspend': num_underspend,
        'total_projected_loss': total_projected_loss,
        'num_outstanding_90_days': num_outstanding_90_days,
        'flagged_accounts': flagged_accounts,
        'members': members,
        'teams': teams,
        'roles': roles,
        'years': years,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'selected': selected,
        'load_everything': load_everything
    }

    return render(request, 'user_management/profile/dashboard.html', context)


@login_required
def new_member(request):
    # Authenticate if staff or not
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')
    if request.method == 'GET':
        teams = Team.objects.all()
        roles = Role.objects.all()
        skills = Skill.objects.all()
        existing_users = User.objects.filter(member__isnull=True)
        skill_options = [0, 1, 2, 3]

        context = {
            'teams': teams,
            'roles': roles,
            'skills': skills,
            'existingUsers': existing_users,
            'skillOptions': skill_options
        }

        return render(request, 'user_management/new_member.html', context)
    elif request.method == 'POST':

        # Check if we are creating a new user or using an existing one
        use_existing_user = True

        # This should be improved
        if int(request.POST.get('existing_user')) == 0:
            use_existing_user = False

        if use_existing_user:
            user_id = request.POST.get('existing_user')
            user = User.objects.get(id=user_id)
        else:
            # First we make a user, then we make a member
            username = request.POST.get('username')
            password = request.POST.get('password')
            hashed_password = make_password(password)
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            is_staff = request.POST.get('is_staff')

            # Check if that username is already in use
            is_username_taken = User.objects.filter(username__iexact=username).exists()
            is_email_taken = User.objects.filter(email__iexact=email).exists()

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
                user = User(username=username, password=hashed_password, first_name=first_name,
                            last_name=last_name, email=email)

                if is_staff == 'on':
                    user.is_staff = True

        # Now make the member
        # A member can be on many teams
        teams = []
        for team_id in request.POST.getlist('team'):
            teams.append(Team.objects.get(id=team_id))

        role_id = request.POST.get('role')
        role = Role.objects.get(id=role_id)

        # Hours
        buffer_total_percentage = request.POST.get('buffer_total_percentage')
        buffer_learning_percentage = request.POST.get('buffer_learning_percentage')
        buffer_trainers_percentage = request.POST.get('buffer_trainers_percentage')
        buffer_sales_percentage = request.POST.get('buffer_sales_percentage')
        buffer_planning_percentage = request.POST.get('buffer_planning_percentage')
        buffer_internal_percentage = request.POST.get('buffer_internal_percentage')
        buffer_seniority_percentage = request.POST.get('buffer_seniority_percentage')

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
            skill_value = request.POST.get('skill_' + skill.name)
            if skill_value is None:
                skill_value = 0

            SkillEntry.objects.create(skill=skill, member=member, score=skill_value)

        return redirect('/user_management/members')
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def edit_member(request, id):
    # Authenticate if staff or not
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'POST':

        # Member to update
        member = get_object_or_404(Member, id=id)

        # User parameters
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        is_staff = request.POST.get('is_staff') == 'on'

        # Member parameters
        # Now make the member
        # A member can be on many teams
        teams = []
        for team_id in request.POST.getlist('team'):
            teams.append(Team.objects.get(id=team_id))

        role_id = request.POST.get('role')
        role = Role.objects.get(id=role_id)

        # Hours
        buffer_total_percentage = request.POST.get('buffer_total_percentage')
        buffer_learning_percentage = request.POST.get('buffer_learning_percentage')
        buffer_trainers_percentage = request.POST.get('buffer_trainers_percentage')
        buffer_sales_percentage = request.POST.get('buffer_sales_percentage')
        buffer_planning_percentage = request.POST.get('buffer_planning_percentage')
        buffer_internal_percentage = request.POST.get('buffer_internal_percentage')
        buffer_seniority_percentage = request.POST.get('buffer_seniority_percentage')

        # Update skills
        skills = Skill.objects.all()
        for skill in skills:
            skill_score = request.POST.get('skill_' + skill.name)
            try:
                skill_entry = SkillEntry.objects.get(skill=skill, member=member)
            except SkillEntry.DoesNotExist:
                skill_entry = SkillEntry(skill=skill, member=member)

            skill_entry.score = skill_score
            skill_entry.save()

        # Set all of the member skills with the edited variables
        # User parameters
        member.user.first_name = first_name
        member.user.last_name = last_name
        member.user.email = email
        member.user.is_staff = is_staff

        # Member parameters
        member.team.set(teams)
        member.role = role

        # Hours
        member.buffer_total_percentage = buffer_total_percentage
        member.buffer_learning_percentage = buffer_learning_percentage
        member.buffer_trainers_percentage = buffer_trainers_percentage
        member.buffer_sales_percentage = buffer_sales_percentage
        member.buffer_planning_percentage = buffer_planning_percentage
        member.buffer_internal_percentage = buffer_internal_percentage
        member.buffer_seniority_percentage = buffer_seniority_percentage

        member.user.save()
        member.save()

        return redirect('/user_management/members')
    else:
        member = Member.objects.get(id=id)
        teams = Team.objects.all()
        roles = Role.objects.all()
        member_skills = SkillEntry.objects.filter(member=member)
        skill_options = [0, 1, 2, 3]

        context = {
            'member': member,
            'teams': teams,
            'roles': roles,
            'member_skills': member_skills,
            'skillOptions': skill_options
        }

        return render(request, 'user_management/edit_member.html', context)


@login_required
def teams(request):
    teams = Team.objects.all()

    context = {
        'teams': teams,
    }

    return render(request, 'user_management/teams.html', context)


@login_required
def new_team(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')
    if request.method == 'POST':
        context = {}
        return JsonResponse(context)
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def edit_team(request):
    if request.method == 'POST':
        pass
    else:
        return HttpResponse('You are at the wrong place')


@login_required
def members_single(request, id=0):
    """
    Main profile page (accounts)
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id and id != 0:
        return HttpResponseForbidden('You do not have permission to view this page')

    if id == 0:  # This is a profile page
        member = Member.objects.get(user=request.user)
    else:
        member = Member.objects.get(id=id)

    """
    We store all the account information in a master dictionary, with flags for each account's association
    to this member (eg. backup/mandate). When assigning the hours for each account, we check against these same
    flags for whatever custom assignment needs to be done (eg. mandates are assigned differently, backups have 
    additional hours)
    """
    master_accounts_dictionary = {}
    active_accounts = Client.objects.filter(
        Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
        Q(am1=member) | Q(am2=member) | Q(am3=member) |
        Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
        Q(strat1=member) | Q(strat2=member) | Q(strat3=member), status=1
    )
    for account in active_accounts:
        if account.id not in master_accounts_dictionary:
            master_accounts_dictionary[account.id] = {}
            master_accounts_dictionary[account.id]['account'] = account
            master_accounts_dictionary[account.id]['is_active'] = True
            master_accounts_dictionary[account.id]['is_mandate'] = False
            master_accounts_dictionary[account.id]['is_onboarding'] = False
            master_accounts_dictionary[account.id]['is_backup'] = False
            master_accounts_dictionary[account.id]['is_flagged'] = False

    onboarding_accounts = Client.objects.filter(
        Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
        Q(am1=member) | Q(am2=member) | Q(am3=member) |
        Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
        Q(strat1=member) | Q(strat2=member) | Q(strat3=member), status=0
    )
    for account in onboarding_accounts:
        if account.id not in master_accounts_dictionary:
            master_accounts_dictionary[account.id] = {}
            master_accounts_dictionary[account.id]['account'] = account
            master_accounts_dictionary[account.id]['is_active'] = False
            master_accounts_dictionary[account.id]['is_mandate'] = False
            master_accounts_dictionary[account.id]['is_backup'] = False
            master_accounts_dictionary[account.id]['is_flagged'] = False
        master_accounts_dictionary[account.id]['is_onboarding'] = True

    for account in member.backup_accounts:
        if account.id not in master_accounts_dictionary:
            master_accounts_dictionary[account.id] = {}
            master_accounts_dictionary[account.id]['account'] = account
            master_accounts_dictionary[account.id]['is_active'] = False
            master_accounts_dictionary[account.id]['is_mandate'] = False
            master_accounts_dictionary[account.id]['is_flagged'] = False
            master_accounts_dictionary[account.id]['is_onboarding'] = False
        master_accounts_dictionary[account.id]['is_backup'] = True

    for assignment in member.active_mandate_assignments:
        account = assignment.mandate.account
        if account.id not in master_accounts_dictionary:
            master_accounts_dictionary[account.id] = {}
            master_accounts_dictionary[account.id]['account'] = account
            master_accounts_dictionary[account.id]['is_active'] = False
            master_accounts_dictionary[account.id]['is_onboarding'] = False
            master_accounts_dictionary[account.id]['is_backup'] = False
            master_accounts_dictionary[account.id]['is_flagged'] = False
        if 'assignments' not in master_accounts_dictionary[account.id]:
            master_accounts_dictionary[account.id]['assignments'] = []
        master_accounts_dictionary[account.id]['is_mandate'] = True
        master_accounts_dictionary[account.id]['assignments'].append(assignment)

    flagged_accounts = Client.objects.filter(star_flag=True, flagged_assigned_member=member)
    for account in flagged_accounts:
        if account.id not in master_accounts_dictionary:
            master_accounts_dictionary[account.id] = {}
            master_accounts_dictionary[account.id]['account'] = account
            master_accounts_dictionary[account.id]['is_active'] = False
            master_accounts_dictionary[account.id]['is_mandate'] = False
            master_accounts_dictionary[account.id]['is_onboarding'] = False
            master_accounts_dictionary[account.id]['is_backup'] = False
        master_accounts_dictionary[account.id]['is_flagged'] = True

    account_hours = {}
    account_allocation = {}
    for account_id in master_accounts_dictionary:
        account_dict = master_accounts_dictionary[account_id]
        account_hours[account_id] = 0
        account_allocation[account_id] = 0
        account = account_dict['account']
        if account_dict['is_active']:
            hours = account.get_hours_worked_this_month_member(member)
            allocation = account.get_allocation_this_month_member(member)
            account_hours[account_id] += hours
            account_allocation[account_id] += allocation
        if account_dict['is_mandate']:
            for assignment in master_accounts_dictionary[account.id]['assignments']:
                hours = assignment.worked_this_month
                allocation = assignment.hours
                account_hours[account_id] += hours
                account_allocation[account_id] += allocation
        if account_dict['is_backup']:
            hours = account.get_hours_worked_this_month_member(member)
            allocation = account.get_allocation_this_month_member(member, is_backup_account=True)
            account_hours[account_id] += hours
            account_allocation[account_id] += allocation
        if account_dict['is_onboarding']:
            hours = account.onboarding_hours_worked(member)
            allocation = account.onboarding_hours_allocated(member)
            account_hours[account_id] += hours
            account_allocation[account_id] += allocation

    # TODOS, handle possible get by date
    today = datetime.datetime.today().date()
    todos = Todo.objects.filter(member=member, completed=False, date_created=today)

    onboarding_steps = OnboardingStep.objects.all()

    # sort by account name alphabetical
    sorted_dict = sorted(master_accounts_dictionary.items(), key=lambda kv: kv[1]['account'].client_name)

    context = {
        'account_hours': account_hours,
        'account_allocation': account_allocation,
        'member': member,
        'master_accounts_dictionary': sorted_dict,
        'today': today,
        'todos': todos,
        'flagged_accounts_count': flagged_accounts.count(),
        'onboarding_steps': onboarding_steps,
        'title': 'Dashboard - SparkView'
    }

    # ajax mandate completed checkmarking and todolist completion
    if request.method == 'POST':
        checked = request.POST.get('checked') == 'true'
        mandate_id = request.POST.get('mandate_id')
        if mandate_id is not None:
            mandate = Mandate.objects.get(id=mandate_id)
            mandate.completed = checked
            mandate.save()

        todo_id = request.POST.get('todo_id')
        if todo_id is not None:
            todo = Todo.objects.get(id=todo_id)
            todo.completed = True
            todo.save()

        return HttpResponse()

    return render(request, 'user_management/profile/profile_refactor.html', context)


@login_required
def members_single_hours(request, id):
    """
    Hours page for individual member
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = Member.objects.get(id=id)

    context = {
        'member': member
    }

    return render(request, 'user_management/profile/hours.html', context)


@login_required
def members_single_reports(request, id):
    """
    Reports page for individual member
    :param request:
    :param id:
    :return:
    """
    member = Member.objects.get(id=id)
    if not request.user.is_staff and int(id) != member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'no_report':
            no_report_acc_id = request.POST.get('account_id')
            no_report_month = request.POST.get('month')
            no_report_year = request.POST.get('year')

            account = Client.objects.get(id=no_report_acc_id)
            if account not in member.accounts and not member.user.is_staff:
                return HttpResponse('Permission denied m8')
            report = MonthlyReport.objects.get(account=account, month=no_report_month, year=no_report_year)
            report.no_report = True
            report.save()

            # return redirect('')
        else:
            return HttpResponse('Invalid action')

    now = datetime.datetime.now()
    month = now.month
    last_month = month - 1
    year = now.year
    reporting_period = now.day <= 31
    reports = []

    accounts = Client.objects.filter(
        Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
        Q(am1=member) | Q(am2=member) | Q(am3=member) |
        Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
        Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
    ).filter(status=1) | member.backup_accounts

    first_weekday, days_in_month = calendar.monthrange(now.year, now.month)

    if reporting_period:
        if last_month == 0:
            last_month = 12
        if now.day == days_in_month:
            last_month = month  # Last day of month, show the current month so we can set stuff
        # TODO: Fix the following boiler plate
        for account in accounts:
            report, created = MonthlyReport.objects.get_or_create(account=account, month=last_month, year=year)
            if created:
                if account.tier == 1 or account.advanced_reporting:
                    report.report_type = 2  # Advanced
                else:
                    report.report_type = 1  # Standard
                report.save()
            if not report.no_report:
                reports.append(report)
        for account in member.inactive_lost_accounts_last_month:
            report, created = MonthlyReport.objects.get_or_create(account=account, month=last_month, year=year)
            if created:
                if account.tier == 1 or account.advanced_reporting:
                    report.report_type = 2  # Advanced
                else:
                    report.report_type = 1  # Standard
                report.save()
            if not report.no_report:
                reports.append(report)

    reports.sort(key=lambda r: (r.due_date is None, r.due_date))  # forces reports w/o due dates to the end

    context = {
        'member': member,
        'reports': reports,
        'last_month_str': calendar.month_name[last_month],
        'reporting_month': last_month,
        'reporting_year': year,
        'title': 'Reports'
    }

    return render(request, 'user_management/profile/reports_refactor.html', context)


@login_required
def members_single_promos(request, id):
    """
    Promos page for individual member
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = Member.objects.get(id=id)
    now = datetime.datetime.now()
    accounts = Client.objects.filter(
        Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
        Q(am1=member) | Q(am2=member) | Q(am3=member) |
        Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
        Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
    ).filter(status=1).order_by('client_name')
    seven_days_ago = now - datetime.timedelta(7)

    promos = Promo.objects.filter(account__in=accounts, end_date__gte=seven_days_ago)

    context = {
        'member': member,
        'promos': promos,
        'title': 'Promos - SparkView'
    }

    return render(request, 'user_management/profile/promos_refactor.html', context)


@login_required
def members_single_kpis(request, id):
    """
    KPIs page for individual member
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = Member.objects.get(id=id)
    accounts = Client.objects.filter(
        Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
        Q(am1=member) | Q(am2=member) | Q(am3=member) |
        Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
        Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
    ).filter(status=1).order_by('client_name')

    context = {
        'member': member,
        'accounts': accounts
    }

    return render(request, 'user_management/profile/kpis.html', context)


@login_required
def members_single_timesheet(request, id):
    """
    Timesheet page for individual member
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = Member.objects.get(id=id)
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    reg_hours_this_month = AccountHourRecord.objects.filter(member=member, month=month, year=year, is_unpaid=False)
    mandate_hours_this_month = MandateHourRecord.objects.filter(assignment__member=member, month=month, year=year)
    value_added_hours = AccountHourRecord.objects.filter(member=member, month=month, year=year, is_unpaid=True)

    trainer_hours_this_month = TrainingHoursRecord.objects.filter(trainer=member, month=month, year=year)
    trainee_hours_this_month = TrainingHoursRecord.objects.filter(trainee=member, month=month, year=year)

    trainee_hour_total = 0.0
    for trainee_hour in trainee_hours_this_month:
        trainee_hour_total += trainee_hour.hours

    context = {
        'member': member,
        'reg_hours_this_month': reg_hours_this_month,
        'trainer_hours_this_month': trainer_hours_this_month,
        'trainee_hours_this_month': trainee_hours_this_month,
        'mandate_hours_this_month': mandate_hours_this_month,
        'trainee_hour_total': trainee_hour_total,
        'value_added_hours': value_added_hours,
        'title': 'Timesheet'
    }

    return render(request, 'user_management/profile/timesheet_refactor.html', context)


@login_required
def members_single_skills(request, id):
    """
    Skills page for individual member
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = Member.objects.get(id=id)
    member_groups = [group for group in TrainingGroup.objects.all() if member in group.all_members]

    score_badges = ['secondary', 'dark', 'danger', 'warning', 'success']

    context = {
        'member': member,
        'score_badges': score_badges,
        'member_groups': member_groups
    }

    return render(request, 'user_management/profile/skills.html', context)


@login_required
def member_oops(request, id):
    """
    Oops reports that belong to the member
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = get_object_or_404(Member, id=id)
    oops = member.incident_members.filter(approved=True)
    incidents_reported = Incident.objects.filter(reporter=member)

    context = {
        'member': member,
        'incidents': oops,
        'incidents_reported': incidents_reported
    }

    return render(request, 'user_management/profile/oops.html', context)


@login_required
def performance(request, member_id):
    """
    Oops reports, high fives, and skills page
    """

    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(member_id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = get_object_or_404(Member, id=member_id)
    oops = member.incident_members.filter(approved=True)
    oops_reported = Incident.objects.filter(reporter=member)
    high_fives = HighFive.objects.filter(member=member_id)

    tag_colors = ['', 'is-dark', 'is-danger', 'is-warning', 'is-success']
    skill_categories = SkillCategory.objects.all()
    member_skills_categories = []  # list of objects where each object encodes info about a skill category
    for cat in skill_categories:
        skill_entries = SkillEntry.objects.filter(skill__skill_category=cat, member=member)
        member_skills_categories.append({
            'name': cat.name,
            'skill_entries': skill_entries,
            'average': skill_entries.aggregate(Sum('score'))['score__sum'] / skill_entries.count()
        })

    badges = SkillEntry.objects.filter(member=member, score=4)

    context = {
        'member': member,
        'oops': oops,
        'oops_reported': oops_reported,
        'high_fives': high_fives,
        'title': 'Performance',
        'tag_colors': tag_colors,
        'skills': skills,
        'member_skills_categories': member_skills_categories,
        'badges': badges
    }

    return render(request, 'user_management/profile/performance.html', context)


@login_required
def member_high_fives(request, id):
    """
    High five reports that belong to the member
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    member = Member.objects.get(id=id)
    high_fives = HighFive.objects.filter(member=id)

    context = {
        'member': member,
        'high_fives': high_fives
    }

    return render(request, 'user_management/profile/highfives.html', context)


@login_required
def input_hours_profile(request, id):
    """
    Alternative way for members to report hours
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)
    if not request.user.is_staff and int(id) != request_member.id:
        return HttpResponseForbidden('You do not have permission to view this page')

    # if provided member ID is invalid, use request user
    try:
        member = Member.objects.get(id=id)
    except Member.DoesNotExist:
        raise Http404('The member associated with this ID does not exist!')

    if request.method == 'GET':
        accounts = list(Client.objects.filter(
            Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
            Q(am1=member) | Q(am2=member) | Q(am3=member) |
            Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
            Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
        ).filter(Q(status=0) | Q(status=1)).order_by('client_name'))
        non_backups_length = len(accounts)  # for knowing where the backup accounts are in the list

        accounts.extend(list(member.backup_accounts))  # add backup accounts

        all_accounts = Client.objects.all().order_by('client_name')

        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
        now = datetime.datetime.now()
        years = [i for i in range(2018, now.year + 1)]

        monthnow = now.month
        current_year = now.year

        members = Member.objects.none
        if request.user.is_staff:
            # Reason for this is that this members list if used for the training hours, which is staff only
            members = Member.objects.filter(deactivated=False).order_by('user__first_name')

        # for mandate hour inputting
        mandate_assignments = member.active_mandate_assignments

        context = {
            'member': member,
            'all_accounts': all_accounts,
            'accounts': accounts,
            'non_backups_length': non_backups_length,
            'months': months,
            'monthnow': monthnow,
            'years': years,
            'members': members,
            'current_year': current_year,
            'mandate_assignments': mandate_assignments,
            'title': 'Input Hours'
        }

        return render(request, 'user_management/profile/input_hours_refactor.html', context)

    elif request.method == 'POST':
        accounts = Client.objects.filter(
            Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
            Q(am1=member) | Q(am2=member) | Q(am3=member) |
            Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
            Q(strat1=member) | Q(strat2=member) | Q(strat3=member)
        ).filter(Q(status=0) | Q(status=1)).order_by('client_name') | member.backup_accounts
        accounts_count = accounts.count()

        for i in range(accounts_count):
            i = str(i)
            account_id = request.POST.get('account-id-' + i)
            if account_id is None:
                continue  # ajax request for just one account
            account = Client.objects.get(id=account_id)

            if not request.user.is_staff and not request_member.has_account(account_id):
                return HttpResponseForbidden('You do not have permission to add hours to this account')
            hours = request.POST.get('hours-' + i)
            try:
                hours = float(hours)
            except (TypeError, ValueError):
                continue
            month = request.POST.get('month-' + i)
            year = request.POST.get('year-' + i)

            is_onboarding = account.status == 0
            AccountHourRecord.objects.create(member=member, account=account, hours=hours, month=month, year=year,
                                             is_onboarding=is_onboarding)

        return redirect('/user_management/members/' + str(member.id) + '/input_hours')


@login_required
def input_mandate_profile(request, id):
    """
    Alternative way for members to report hours
    :param request:
    :param id:
    :return:
    """
    request_member = Member.objects.get(user=request.user)

    if request.method == 'POST':
        # if provided member ID is invalid, use request user
        try:
            member = Member.objects.get(id=id)
        except Member.DoesNotExist:
            raise Http404('The member associated with this ID does not exist!')

        assignments = member.active_mandate_assignments
        for i in range(len(assignments)):
            assignment = assignments[i]
            i = str(i)

            # check if this assignment is in the request user's active assignments, if not then disallow post
            if not request.user.is_staff and assignment not in request_member.active_mandate_assignments:
                return HttpResponseForbidden('You do not have permission to add hours to this account')
            hours = request.POST.get('hours-' + i)
            try:
                hours = float(hours)
            except (TypeError, ValueError):
                continue
            month = request.POST.get('month-' + i)
            year = request.POST.get('year-' + i)

            completed_str = request.POST.get('completed-' + i)
            completed = True if completed_str is not None else False
            mandate = assignment.mandate
            mandate.completed = completed
            mandate.save()

            is_onboarding = mandate.account.status == 0
            MandateHourRecord.objects.create(assignment=assignment, hours=hours, month=month, year=year,
                                             is_onboarding=is_onboarding)

        return redirect('/user_management/members/' + str(member.id) + '/input_hours')


@login_required
def training_members(request):
    """
    View of all members skills and training groups
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'GET':
        training_groups = TrainingGroup.objects.all()

        score_badges = ['secondary', 'dark', 'danger', 'warning', 'success']
        scores = SkillEntry.SCORE_OPTIONS

        context = {
            'training_groups': training_groups,
            'score_badges': score_badges,
            'scores': scores
        }

        return render(request, 'user_management/training.html', context)
    elif request.method == 'POST':
        member_id = request.POST.get('member-id')
        skill_id = request.POST.get('skill-id')
        new_score = request.POST.get('new-score')

        try:
            new_score = int(new_score)
        except ValueError:
            return HttpResponse('Invalid score value!')

        member = get_object_or_404(Member, id=member_id)
        skill_entry = get_object_or_404(SkillEntry, id=skill_id)

        skill_entry.score = new_score
        skill_entry.save()

        # create todo for member
        description = 'Your skill ranking for ' + skill_entry.skill.name + \
                      ' has been updated! Head over to the performance tab to view it.'
        link = '/user_management/members/' + member_id + '/performance'
        Todo.objects.create(member=member, description=description, link=link, type=2)

        # store skill history for this entry
        SkillHistory.objects.create(skill_entry=skill_entry)

        return redirect('/user_management/members/training')


@login_required
def training_members_json(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    members = list(Member.objects.values())
    return JsonResponse(members, safe=False)


@login_required
def skills(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    all_skills = Skill.objects.all()

    context = {
        'skills': all_skills
    }

    return render(request, 'user_management/skills.html', context)


@login_required
def skills_single(request, id):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    skill = Skill.objects.get(id=id)

    context = {
        'skill': skill
    }

    return render(request, 'user_management/skills_single.html', context)


@login_required
def skills_new(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'POST':
        skill_name = request.POST.get('skillname')
        Skill.objects.create(name=skill_name)

        return redirect('/user_management/skills')
    else:
        return HttpResponse('Invalid request type')


@login_required
def view_summary(request):
    member = Member.objects.get(user=request.user)
    today = datetime.date.today()
    member.last_viewed_summary = today
    member.save()

    return HttpResponse()


@login_required
def backups(request):
    """
    This will be the active backup page. It can have a sidebar to go to non active backups
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'POST':
        # Creates a backup period
        form_type = request.POST.get('type')
        if form_type == 'period':
            member_id = request.POST.get('member')
            try:
                member = Member.objects.get(id=member_id)
            except Member.DoesNotExist:
                return HttpResponse('Member does not exist')

            start_date = datetime.datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
            end_date = datetime.datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')

            bp = BackupPeriod()
            bp.member = member
            bp.start_date = start_date
            bp.end_date = end_date
            bp.save()

            accounts = member.onboard_active_accounts
            for account in accounts:
                b = Backup()
                b.account = account
                b.period = bp
                b.save()

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
            return HttpResponse()
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
        elif form_type == 'expand':
            bp_id = request.POST.get('period')
            bp = BackupPeriod.objects.get(id=bp_id)

            bs = bp.backup_set.all()

            bsj = {}
            count = 0

            for b in bs:
                bsj[count] = {}
                bsj[count]['bu_id'] = b.id
                bsj[count]['bu_str'] = str(b)
                bsj[count]['member_id'] = b.member.id
                bsj[count]['member_name'] = b.member.user.get_full_name()
                bsj[count]['account_id'] = b.account.id
                bsj[count]['account_name'] = b.account.client_name
                if b.bc_link is None or b.bc_link == '':
                    bsj[count]['bc_link'] = 'None'
                else:
                    bsj[count]['bc_link'] = b.bc_link
                bsj[count]['approved'] = b.approved
                bsj[count]['row_id'] = bp.id
                count += 1

            return JsonResponse(bsj)

        return redirect('/user_management/backups')

    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(7)
    members = Member.objects.filter(deactivated=False).order_by('user__first_name')
    accounts = Client.objects.filter(Q(status=0) | Q(status=1)).order_by('client_name')

    active_backups = BackupPeriod.objects.filter(start_date__lte=now, end_date__gte=now).order_by('-end_date')
    non_active_backup_periods = BackupPeriod.objects.exclude(end_date__lte=seven_days_ago).exclude(start_date__lte=now,
                                                                                                   end_date__gte=now)

    context = {
        'members': members,
        'accounts': accounts,
        'active_backups': active_backups,
        'non_active_backup_periods': non_active_backup_periods
    }

    return render(request, 'user_management/backup.html', context)


@login_required
def backup_event(request, backup_period_id):
    """
    Specific backup event page
    :param request:
    :param backup_period_id:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    try:
        backup_period = BackupPeriod.objects.get(id=backup_period_id)
    except BackupPeriod.DoesNotExist:
        return HttpResponse('That backup period does not exist')

    if request.method == 'POST':
        form_type = request.POST.get('type')
        if form_type == 'backup':
            member_ids = request.POST.getlist('members')
            members = Member.objects.filter(id__in=member_ids)
            account_id = request.POST.get('account')
            try:
                account = Client.objects.get(id=account_id)
            except Client.DoesNotExist:
                return HttpResponse('This client has not exist (this might be a bug, please report to Sam or Lexi)')
            bp_id = request.POST.get('period')
            # bp = BackupPeriod.objects.get(id=bp_id)
            bc_link = request.POST.get('bc_link')

            bu_id = request.POST.get('bu_id_add')
            try:
                b = Backup.objects.get(id=bu_id)
            except Backup.DoesNotExist:
                return HttpResponse('That backup does not exist')
            b.account = account
            b.members.set(members)
            b.bc_link = bc_link
            b.save()

        if form_type == 'approve':
            bu_id = request.POST.get('bu_id')

            approved_by = Member.objects.get(user=request.user)

            b = Backup.objects.get(id=bu_id)
            b.approved = True
            b.approved_by = approved_by
            b.save()

            return HttpResponse('success')

    role = backup_period.member.role
    members = Member.objects.filter(role=role, deactivated=False).exclude(id=backup_period.member.id).order_by(
        'user__first_name')

    context = {
        'backup_period': backup_period,
        'members': members
    }

    return render(request, 'user_management/backup_event.html', context)


@login_required
def add_training_hours(request):
    """
    Adds a training hour record
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    # trainer_id = request.POST.get('trainer_id')
    trainer = Member.objects.get(user=request.user)

    trainee_ids = request.POST.getlist('trainee_id')
    trainees = Member.objects.filter(id__in=trainee_ids, deactivated=False).order_by('user__first_name')

    if trainer in trainees:
        return HttpResponse('You can\'t train yourself!')

    month = request.POST.get('month')
    year = request.POST.get('year')
    hours = request.POST.get('hours')

    for trainee in trainees:
        TrainingHoursRecord.objects.create(trainee=trainee, trainer=trainer, month=month, year=year, hours=hours)

    # return redirect('/clients/accounts/report_hours')
    # keep everything on profile page
    return redirect('/user_management/members/' + str(trainer.id) + '/input_hours')


@login_required
def late_onboard(request):
    """
    Records reason for late onboarding
    :param request:
    :return:
    """
    account_id = request.POST.get('account_id')
    account = Client.objects.get(id=account_id)

    message = request.POST.get('late_reason')
    account.late_onboard_reason = message
    account.save()

    return redirect('/user_management/profile')
