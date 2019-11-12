from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.core.mail import send_mail
from bloom.settings import TEMPLATE_DIR, EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from user_management.models import Member, Team, Incident, Role, HighFive, IncidentReason, InternalOops, \
    MemberDashboardSnapshot
from adwords_dashboard.models import BadAdAlert
from client_area.models import AccountAllocatedHoursHistory, AccountHourRecord, Promo, MonthlyReport, Opportunity, Tag, \
    ClientDashboardSnapshot
from budget.models import Client, AccountBudgetSpendHistory, TierChangeProposal, SalesProfile
from notifications.models import Notification, Todo
from django.conf import settings
import datetime
import calendar


@login_required
def agency_overview(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    # Get account related metrics
    total_active_accounts = Client.objects.filter(status=1).order_by('client_name')
    total_active_seo = Client.objects.filter(status=1).filter(salesprofile__seo_status=1).count()
    total_active_cro = Client.objects.filter(status=1).filter(salesprofile__seo_status=1).count()

    total_onboarding = Client.objects.filter(status=0).count()
    total_inactive = Client.objects.filter(status=2).count()
    total_lost = Client.objects.filter(status=3).count()

    incident_count = Incident.objects.all().count()

    # Members
    members = Member.objects.all().order_by('user__first_name')

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0

    for member in members:
        actual_aggregate += member.actual_hours_this_month
        allocated_aggregate += member.allocated_hours_month()
        available_aggregate += member.hours_available

    if allocated_aggregate + available_aggregate == 0:
        capacity_rate = 0
    else:
        capacity_rate = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

    if allocated_aggregate == 0:
        utilization_rate = 0
    else:
        utilization_rate = 100 * (actual_aggregate / allocated_aggregate)

    # sorted_members_by_count = sorted(members, key=lambda t: t.incidents)

    # Total management fee
    # total_management_fee = 0.0
    total_allocated_hours = 0.0

    for aa in total_active_accounts:
        # total_management_fee += aa.total_fee
        total_allocated_hours += aa.all_hours

    # hours worked this month
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    total_hours_worked = \
        AccountHourRecord.objects.filter(month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
    if total_hours_worked is None:
        total_hours_worked = 0.0

    try:
        allocation_ratio = total_hours_worked / total_allocated_hours
    except ZeroDivisionError:
        allocation_ratio = 0.0

    context = {
        'title': 'Agency Overview',
        'total_active_accounts': total_active_accounts.count(),
        'total_active_seo': total_active_seo,
        'total_active_cro': total_active_cro,
        'total_onboarding': total_onboarding,
        'total_inactive': total_inactive,
        'total_lost': total_lost,
        'capacity_rate': capacity_rate,
        'utilization_rate': utilization_rate,
        'incident_count': incident_count,
        # 'top_offenders': sorted_members_by_count,
        'allocation_ratio': allocation_ratio,
        'total_allocated_hours': total_allocated_hours,
        'total_hours_worked': total_hours_worked,
        'actual_aggregate': actual_aggregate,
        'allocated_aggregate': allocated_aggregate,
        'available_aggregate': available_aggregate,
        'members': members
    }

    return render(request, 'reports/agency_overview_refactor.html', context)


@login_required
def account_spend_progression(request):
    """
    Creates the report that warns about accounts that may lose values
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')
    accounts = Client.objects.filter(status=1).order_by('client_name')

    total_projected_loss = 0.0
    total_projected_overspend = 0.0
    for account in accounts:
        if account.projected_loss < 0:  # we will overspend
            total_projected_overspend += account.project_yesterday - account.current_budget
        else:  # we will underspend
            total_projected_loss += account.projected_loss

    context = {
        'title': 'PPC Account Spend Progression',
        'accounts': accounts,
        'total_projected_loss': total_projected_loss,
        'total_projected_overspend': total_projected_overspend
    }

    return render(request, 'reports/account_spend_progression_refactor.html', context)


def build_member_stats_from_members(members, selected_month, selected_year, historical=False):
    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0
    lifespan_aggregate = 0.0
    members_stats = []

    for member in members:
        if not historical:
            actual_aggregate += member.actual_hours_this_month
            allocated_aggregate += member.allocated_hours_this_month
            available_aggregate += member.hours_available
            lifespan_aggregate += member.lifespan(datetime.date.today())

            actual_hours = member.actual_hours_this_month
            allocated_hours = member.allocated_hours_this_month
            available_hours = member.hours_available
            utilization_rate = member.utilization_rate
            capacity_rate = member.capacity_rate
            value_added_hours = member.value_added_hours_this_month
            active_accounts_count = member.active_accounts_including_backups_count
            onboarding_accounts_count = member.onboarding_accounts_count
            backup_hours_plus_minus = member.backup_hours_plus_minus
            last_updated_hours = member.last_updated_hours
            outstanding_ninety_days = member.phase_tasks.count
            seniority_buffer = member.seniority_buffer(selected_month, selected_year)
            training_hours_assigned = member.training_hours_assigned
        else:
            actual_aggregate += member.actual_hours_other_month(selected_month, selected_year)
            allocated_aggregate += member.allocated_hours_other_month(selected_month, selected_year)
            available_aggregate += member.hours_available_other_month(selected_month, selected_year)
            date = datetime.date(selected_year, selected_month,
                                 calendar.monthrange(selected_year, selected_month)[1])
            lifespan_aggregate += member.lifespan(date)

            actual_hours = member.actual_hours_other_month(selected_month, selected_year)
            allocated_hours = member.allocated_hours_other_month(selected_month, selected_year)
            available_hours = member.hours_available_other_month(selected_month, selected_year)
            utilization_rate = member.utilization_rate_other_month(selected_month, selected_year)
            capacity_rate = member.capacity_rate_other_month(selected_month, selected_year)
            value_added_hours = member.value_added_hours_other_month(selected_month, selected_year)
            active_accounts_count = member.active_accounts_including_backups_count_other_month(selected_month,
                                                                                               selected_year)
            onboarding_accounts_count = member.onboarding_accounts_count_other_month(selected_month, selected_year)
            backup_hours_plus_minus = member.backup_hours_plus_minus_other_month(selected_month, selected_year)
            last_updated_hours = 'N/A'
            outstanding_ninety_days = member.phase_tasks_other_month(selected_month, selected_year).count()
            seniority_buffer = member.seniority_buffer(selected_month, selected_year)
            training_hours_assigned = member.training_hours_assigned_other_month(selected_month, selected_year)

        members_stats.append({
            'member': member,
            'actual_hours': actual_hours,
            'allocated_hours': allocated_hours,
            'available_hours': available_hours,
            'utilization_rate': utilization_rate,
            'capacity_rate': capacity_rate,
            'value_added_hours': value_added_hours,
            'active_accounts_count': active_accounts_count,
            'onboarding_accounts_count': onboarding_accounts_count,
            'backup_hours_plus_minus': backup_hours_plus_minus,
            'last_updated_hours': last_updated_hours,
            'outstanding_ninety_days': outstanding_ninety_days,
            'seniority_buffer': seniority_buffer,
            'training_hours_assigned': training_hours_assigned
        })

    department_stats = {}

    if allocated_aggregate + available_aggregate == 0:
        department_stats['capacity_rate'] = 0
    else:
        department_stats['capacity_rate'] = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

    if allocated_aggregate == 0:
        department_stats['utilization_rate'] = 0
    else:
        department_stats['utilization_rate'] = 100 * (actual_aggregate / allocated_aggregate)

    if len(members) == 0:
        department_stats['average_lifespan'] = 0
    else:
        department_stats['average_lifespan'] = lifespan_aggregate / len(members)
    department_stats.update({
        'actual_aggregate': 0.0,
        'allocated_aggregate': 0.0,
        'available_aggregate': 0.0,
    })

    # spend growth/loss trends
    month_strs = []
    cur_month = selected_month
    cur_year = selected_year
    spends = [0] * 10
    fees = [0] * 10
    for i in range(10):
        month_strs.insert(0, str(calendar.month_name[cur_month]) + ', ' + str(cur_year))
        try:
            snapshot = MemberDashboardSnapshot.objects.get(month=cur_month, year=cur_year)
            spend = snapshot.aggregate_spend
            fee = snapshot.aggregate_fee
        except MemberDashboardSnapshot.DoesNotExist:
            spend = 0.0
            fee = 0.0

        spends[10 - i - 1] = spend
        fees[10 - i - 1] = fee

        cur_month -= 1
        if cur_month == 0:
            cur_month = 12
            cur_year -= 1

    department_stats.update({
        'spends': spends,
        'fees': fees,
        'month_strs': month_strs
    })

    return members_stats, department_stats


def get_members_from_dashboard_type(dashboard):
    """
    Returns the appropriate list of members (cms, ams, or strategists) based on the dashboard type passed in
    """
    if dashboard == 'cm':
        role = Role.objects.filter(
            Q(name='CM') | Q(name='PPC Specialist') | Q(name='PPC Analyst') | Q(name='PPC Intern') | Q(
                name='PPC Team Lead') | Q(name='Team Lead'))
        members = Member.objects.filter(Q(role__in=role) | Q(id=35) | Q(id=25) | Q(id=45)).order_by('user__first_name')
        report_type = title = 'CM Member Dashboard'
    elif dashboard == 'am':
        role = Role.objects.filter(Q(name='AM') | Q(name='Account Coordinator') | Q(name='Account Manager') | Q(
            name='Team Lead - Client Services'))
        members = Member.objects.filter(role__in=role).order_by('user__first_name')
        report_type = title = 'AM Member Dashboard'
    elif dashboard == 'strat':
        role = Role.objects.filter(Q(name='Strategist'))
        members = Member.objects.filter(role__in=role).order_by('user__first_name')
        report_type = title = 'Strat Member Dashboard'
    elif dashboard == 'seo':
        role = Role.objects.filter(
            Q(name='SEO') | Q(name='SEO Analyst') | Q(name='SEO Intern') | Q(name='Team Lead - SEO'))
        members = Member.objects.filter(Q(role__in=role) | Q(id=15)).order_by('user__first_name')
        report_type = title = 'SEO Member Dashboard'
    else:
        return HttpResponseNotFound('Invalid dashboard type!')

    return members, title, report_type


@login_required
def member_dashboard_overview(request):
    """
    Creates report that shows the capacity of the PPC campaign managers on an aggregated and individual basis
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    selected_month = now.month
    selected_year = now.year
    historical = False

    if 'month' in request.GET and 'year' in request.GET and (int(request.GET.get(
            'month')) != selected_month or int(request.GET.get('year')) != selected_year):
        selected_month = int(request.GET.get('month'))
        selected_year = int(request.GET.get('year'))
        historical = True

    dashboard = request.get_full_path().split('/')[2]
    members, title, report_type = get_members_from_dashboard_type(dashboard)
    members_stats, department_stats = build_member_stats_from_members(members, selected_month, selected_year,
                                                                      historical)

    total_seo_hours, total_cro_hours, seo_accounts = 0.0, 0.0, None
    if dashboard == 'seo':
        if not historical:
            seo_accounts = Client.objects.filter(Q(salesprofile__seo_status=1) | Q(salesprofile__cro_status=1)).filter(
                Q(status=0) | Q(status=1)).order_by('client_name')
        else:
            seo_accounts = ClientDashboardSnapshot.objects.filter(Q(has_seo=True) | Q(has_cro=True))
        for account in seo_accounts:
            if account.has_seo:
                total_seo_hours += account.seo_hours
            if account.has_cro:
                total_cro_hours += account.cro_hours

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = [i for i in range(2018, now.year + 1)]
    selected = {
        'month': selected_month,
        'year': selected_year
    }

    context = {
        'title': title,
        'members': members,
        'department_stats': department_stats,
        'report_type': report_type,
        'months': months,
        'years': years,
        'selected': selected,
        'historical': historical,
        'members_stats': members_stats,
        'dashboard': dashboard,
        'total_seo_hours': total_seo_hours,
        'total_cro_hours': total_cro_hours,
        'seo_accounts': seo_accounts
    }

    return render(request, 'reports/member_dashboard_overview.html', context)


@login_required
def member_dashboard_certifications(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    selected_month = now.month
    selected_year = now.year

    if 'month' in request.GET and 'year' in request.GET and (int(request.GET.get(
            'month')) != selected_month or int(request.GET.get('year')) != selected_year):
        selected_month = int(request.GET.get('month'))
        selected_year = int(request.GET.get('year'))

    dashboard = request.get_full_path().split('/')[2]
    members, title, report_type = get_members_from_dashboard_type(dashboard)

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = [i for i in range(2018, now.year + 1)]
    selected = {
        'month': selected_month,
        'year': selected_year
    }

    context = {
        'title': title,
        'report_type': report_type,
        'members': members,
        'months': months,
        'years': years,
        'selected': selected,
        'dashboard': dashboard
    }

    return render(request, 'reports/member_dashboard_certifications.html', context)


@login_required
def member_dashboard_efficiency(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    selected_month = now.month
    selected_year = now.year

    if 'month' in request.GET and 'year' in request.GET and (int(request.GET.get(
            'month')) != selected_month or int(request.GET.get('year')) != selected_year):
        selected_month = int(request.GET.get('month'))
        selected_year = int(request.GET.get('year'))

    dashboard = request.get_full_path().split('/')[2]
    members, title, report_type = get_members_from_dashboard_type(dashboard)

    # top 10 under and over-efficient accounts
    all_accounts = Client.objects.all().order_by('client_name')
    overspenders = []
    underspenders = []
    for account in all_accounts:
        allocated_history = AccountAllocatedHoursHistory.objects.filter(month=selected_month, year=selected_year,
                                                                        account=account).values('account', 'year',
                                                                                                'month').annotate(
            sum_hours=Sum('allocated_hours'))
        allocated_hours = 0.0
        if len(allocated_history) > 0 and 'sum_hours' in allocated_history[0]:
            allocated_hours = allocated_history[0]['sum_hours']

        all_hours = account.all_hours_month_year(selected_month, selected_year)

        if allocated_hours == 0:
            continue

        try:
            actual_hours_ratio = all_hours / allocated_hours
        except ZeroDivisionError:
            actual_hours_ratio = 0.0

        over_members = []
        under_members = []

        loop_items = account.assigned_cms.items()
        if dashboard == 'am':
            loop_items = account.assigned_ams.items()

        for key, value in loop_items:
            if dashboard == 'am':
                member = account.assigned_ams[key]['member']
            else:
                member = account.assigned_cms[key]['member']

            if account.get_hours_remaining_this_month_member(member) < 0:
                over_hours_frequency = len(
                    account.over_under_hours_instances_member(member, selected_month, selected_year, 'over'))
                over_members.append({
                    'member': member,
                    'allocated_hours': account.get_allocation_this_month_member(member),
                    'actual_hours': account.get_hours_worked_this_month_member(member),
                    'over_hours_frequency': over_hours_frequency
                })
            elif account.get_hours_remaining_this_month_member(member) > 0:
                under_hours_frequency = len(
                    account.over_under_hours_instances_member(member, selected_month, selected_year, 'under'))
                under_members.append({
                    'member': member,
                    'allocated_hours': account.get_allocation_this_month_member(member),
                    'actual_hours': account.get_hours_worked_this_month_member(member),
                    'under_hours_frequency': under_hours_frequency
                })

        tmp = {
            'account': account,
            'allocated_hours': allocated_hours,
            'all_hours': all_hours,
            'actual_hours_ratio': actual_hours_ratio,
            'over_members': over_members,
            'under_members': under_members
        }

        if float(actual_hours_ratio) > 1:
            overspenders.append(tmp)
        elif float(actual_hours_ratio) < 1:
            underspenders.append(tmp)
    overspenders.sort(key=lambda x: x['actual_hours_ratio'], reverse=True)
    underspenders.sort(key=lambda x: x['actual_hours_ratio'])
    overspenders = overspenders[:10]
    underspenders = underspenders[:10]

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = [i for i in range(2018, now.year + 1)]
    selected = {
        'month': selected_month,
        'year': selected_year
    }

    context = {
        'title': title,
        'report_type': report_type,
        'members': members,
        'months': months,
        'years': years,
        'selected': selected,
        'dashboard': dashboard,
        'overspenders': overspenders,
        'underspenders': underspenders
    }

    return render(request, 'reports/member_dashboard_efficiency.html', context)


@login_required
def member_dashboard_budgets(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    selected_month = now.month
    selected_year = now.year

    if 'month' in request.GET and 'year' in request.GET and (int(request.GET.get(
            'month')) != selected_month or int(request.GET.get('year')) != selected_year):
        selected_month = int(request.GET.get('month'))
        selected_year = int(request.GET.get('year'))

    dashboard = request.get_full_path().split('/')[2]
    members, title, report_type = get_members_from_dashboard_type(dashboard)

    try:
        snapshot = MemberDashboardSnapshot.objects.get(month=selected_month, year=selected_year)
        outstanding_budget_accounts = snapshot.outstanding_budget_accounts.all()
    except MemberDashboardSnapshot.DoesNotExist:
        outstanding_budget_accounts = None

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = [i for i in range(2018, now.year + 1)]
    selected = {
        'month': selected_month,
        'year': selected_year
    }

    context = {
        'title': title,
        'report_type': report_type,
        'members': members,
        'months': months,
        'years': years,
        'selected': selected,
        'outstanding_budget_accounts': outstanding_budget_accounts,
        'dashboard': dashboard
    }

    return render(request, 'reports/member_dashboard_budgets.html', context)


@login_required
def member_dashboard_new_clients(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    selected_month = now.month
    selected_year = now.year

    if 'month' in request.GET and 'year' in request.GET and (int(request.GET.get(
            'month')) != selected_month or int(request.GET.get('year')) != selected_year):
        selected_month = int(request.GET.get('month'))
        selected_year = int(request.GET.get('year'))

    dashboard = request.get_full_path().split('/')[2]
    members, title, report_type = get_members_from_dashboard_type(dashboard)

    try:
        snapshot = MemberDashboardSnapshot.objects.get(month=selected_month, year=selected_year)
        new_accounts = snapshot.new_accounts.all()
    except MemberDashboardSnapshot.DoesNotExist:
        new_accounts = None

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = [i for i in range(2018, now.year + 1)]
    selected = {
        'month': selected_month,
        'year': selected_year
    }

    context = {
        'title': title,
        'report_type': report_type,
        'members': members,
        'months': months,
        'years': years,
        'selected': selected,
        'new_accounts': new_accounts,
        'dashboard': dashboard
    }

    return render(request, 'reports/member_dashboard_new_clients.html', context)


@login_required
def seo_capacity(request):
    """
    Creates report that shows the capacity of the account managers on an aggregated and individual basis
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    selected_month = now.month
    selected_year = now.year
    historical = False

    if 'month' in request.GET and 'year' in request.GET and (int(request.GET.get(
            'month')) != selected_month or int(request.GET.get('year')) != selected_year):
        selected_month = int(request.GET.get('month'))
        selected_year = int(request.GET.get('year'))
        historical = True

    # Probably has to be changed before production
    role = Role.objects.filter(Q(name='SEO') | Q(name='SEO Analyst') | Q(name='SEO Intern') | Q(name='Team Lead - SEO'))
    members = Member.objects.filter(Q(role__in=role) | Q(id=15)).order_by('user__first_name')

    total_seo_hours = 0.0
    total_cro_hours = 0.0

    status_badges = ['info', 'primary', 'warning', 'danger']
    seo_accounts = Client.objects.filter(Q(salesprofile__seo_status=1) | Q(salesprofile__cro_status=1)).filter(
        Q(status=0) | Q(status=1)).order_by('client_name')

    members_stats, department_stats = build_member_stats_from_members(members, selected_month, selected_year,
                                                                      historical)

    for account in seo_accounts:
        if account.has_seo:
            total_seo_hours += account.seo_hours
        if account.has_cro:
            total_cro_hours += account.cro_hours

    outstanding_budget_accounts = Client.objects.filter(status=1, budget_updated=False)

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years = [i for i in range(2018, now.year + 1)]
    selected = {
        'month': selected_month,
        'year': selected_year
    }

    report_type = 'SEO Member Dashboard'

    context = {
        'title': 'SEO Member Dashboard',
        'members': members,
        'department_stats': department_stats,
        'report_type': report_type,
        'seo_accounts': seo_accounts,
        'status_badges': status_badges,
        'total_seo_hours': total_seo_hours,
        'total_cro_hours': total_cro_hours,
        'outstanding_budget_accounts': outstanding_budget_accounts,
        'members_stats': members_stats,
        'selected': selected,
        'months': months,
        'years': years
    }

    return render(request, 'reports/seo_member_capacity_report_refactor.html', context)


@login_required
def seo_forecasting(request):
    """
    SEO Forecasting
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    context = {
        'title': 'SEO Forecasting - SparkView'
    }

    return render(request, 'reports/seo_forecasting.html', context)


@login_required
def hour_log(request):
    """
    Creates report that shows which users have added hours this month
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    month = now.month
    year = now.year

    members = Member.objects.all().order_by('user__first_name')

    context = {
        'title': 'Hour Log',
        'members': members
    }

    return render(request, 'reports/hour_log_refactor.html', context)


@login_required
def facebook(request):
    """
    Creates report that just shows active FB accounts
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    accounts = Client.objects.exclude(facebook=None).filter(status=1)

    context = {
        'title': 'Facebook',
        'accounts': accounts
    }

    return render(request, 'reports/facebook.html', context)


@login_required
def promos(request):
    """
    Shows calendar of all going on and upcoming promos
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    three_days_ago = datetime.datetime.now() - datetime.timedelta(3)
    three_days_future = datetime.datetime.now() + datetime.timedelta(3)
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(7)
    promos = Promo.objects.filter(end_date__gte=seven_days_ago)

    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(1)
    today_start = datetime.datetime.combine(today, datetime.time())
    today_end = datetime.datetime.combine(tomorrow, datetime.time())

    promos_start_today = Promo.objects.filter(start_date__gte=three_days_ago,
                                              start_date__lte=three_days_future)  # this is really this week
    promos_end_today = Promo.objects.filter(end_date__gte=three_days_ago,
                                            end_date__lte=three_days_future)  # really this week as well

    context = {
        'title': 'Promos',
        'promos': promos,
        'promos_start_today': promos_start_today,
        'promos_end_today': promos_end_today
    }

    return render(request, 'reports/promos_refactor.html', context)


@login_required
def actual_hours(request):
    """
    Shows tables of all hours from selection of members, clients, and month
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    accounts = Client.objects.all().order_by('client_name')
    members = Member.objects.all().order_by('user__first_name')
    months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    years = [str(i) for i in range(2018, now.year)]

    selected = {
        'account': 'all',
        'member': 'all',
        'month': 'all',
        'year': now.year
    }

    if request.method == 'GET':
        hours = AccountHourRecord.objects.filter(year=now.year, month=now.month, is_unpaid=False).values('member',
                                                                                                         'account',
                                                                                                         'year',
                                                                                                         'month').annotate(
            sum_hours=Sum('hours'))
    elif request.method == 'POST':
        year = request.POST.get('year')
        month = request.POST.get('month')
        member = request.POST.get('member')
        account = request.POST.get('account')

        hours = AccountHourRecord.objects.filter()

        if year != 'all':
            hours = hours.filter(year=year)
            selected['year'] = year
        if month != 'all':
            hours = hours.filter(month=month)
            selected['month'] = month
        if member != 'all':
            hours = hours.filter(member=member)
            selected['member'] = int(member)
        if account != 'all':
            hours = hours.filter(account=account)
            selected['account'] = int(account)

        hours = hours.values('member', 'account', 'year', 'month').annotate(sum_hours=Sum('hours'))

    else:
        return HttpResponse('Invalid request type')

    hour_total = 0.0
    for hour in hours:
        try:
            hour['member'] = members.get(id=hour['member'])
        except Member.DoesNotExist:
            hour['member'] = 'Member does not exist'
        try:
            hour['account'] = accounts.get(id=hour['account'])
        except Client.DoesNotExist:
            hour['account'] = 'Client does not exist'

        hour_total += hour['sum_hours']

    context = {
        'title': 'Actual Hours',
        'hours': hours,
        'accounts': accounts,
        'members': members,
        'months': months,
        'years': years,
        'selected': selected,
        'hour_total': hour_total
    }

    return render(request, 'reports/actual_hours_refactor.html', context)


@login_required
def monthly_reporting(request):
    """
    Shows status of reports
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    accounts = Client.objects.all().order_by('client_name')
    teams = Team.objects.all()
    months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    years = ['2018', '2019', '2020']

    selected = {
        'account': 'all',
        'team': 'all',
        'month': 'all',
        'year': now.year
    }

    print(request.method)
    if request.method == 'GET' and not request.GET.get('filter_month'):
        reports = MonthlyReport.objects.filter(year=now.year, month=now.month, no_report=False)
    elif request.method == 'GET':
        year = request.GET.get('year')
        month = request.GET.get('month')
        account_id = request.GET.get('account')
        team_id = request.GET.get('team')

        reports = MonthlyReport.objects.filter(no_report=False)

        if year != 'all':
            reports = reports.filter(year=year)
            selected['year'] = year
        if month != 'all':
            reports = reports.filter(month=month)
            selected['month'] = month
        if team_id != 'all':
            team = Team.objects.get(id=team_id)
            team_accounts = accounts.filter(team=team)
            reports = reports.filter(account__in=team_accounts)
            selected['team'] = int(team_id)
        if account_id != 'all':
            account = Client.objects.get(id=account_id)
            reports = reports.filter(account=account)
            selected['account'] = int(account_id)

    else:
        return HttpResponse('Invalid request type')

    complete_reports = reports.exclude(date_sent_by_am=None).count()
    report_count = reports.count()

    completion_rate = 0.0
    if report_count != 0.0:
        completion_rate = 100.0 * complete_reports / report_count

    ontime_numer = 0.0
    ontime_denom = 0.0
    for report in reports:
        if report.complete_ontime:
            ontime_numer += 1
        ontime_denom += 1

    ontime_rate = 0.0
    if ontime_denom != 0:
        ontime_rate = 100.0 * ontime_numer / ontime_denom

    context = {
        'title': 'Monthly Reporting',
        'reports': reports,
        'accounts': accounts,
        'ontime_pct': ontime_rate,
        'completion_pct': completion_rate,
        'teams': teams,
        'months': months,
        'years': years,
        'selected': selected,
        'date_statuses': MonthlyReport.DATE_STATUSES
    }

    return render(request, 'reports/monthly_reports_refactor.html', context)


@login_required
def account_capacity(request):
    """
    Capacity report for accounts
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    accounts = Client.objects.filter(status=1).order_by('client_name')  # active accounts only

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0

    for account in accounts:
        actual_aggregate += account.hoursWorkedThisMonth
        allocated_aggregate += account.all_hours
        # available_aggregate += member.hours_available

    # if allocated_aggregate + available_aggregate == 0:
    #     capacity_rate = 0
    # else:
    #     capacity_rate = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

    if allocated_aggregate == 0:
        utilization_rate = 0
    else:
        utilization_rate = 100 * (actual_aggregate / allocated_aggregate)

    report_type = 'Account Capacity Report'

    context = {
        'title': 'Account Capacity',
        'accounts': accounts,
        'actual_aggregate': actual_aggregate,
        # 'capacity_rate' : capacity_rate,
        'utilization_rate': utilization_rate,
        'allocated_aggregate': allocated_aggregate,
        # 'available_aggregate' : available_aggregate,
        'report_type': report_type
    }

    return render(request, 'reports/account_capacity_report_refactor.html', context)


@login_required
def backup_report(request):
    """
    Lists accounts that currently have backups
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    context = {}

    return render(request, 'reports/backup_report.html', context)


@login_required
def flagged_accounts(request):
    """
    Lists accounts that currently have backups
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    accounts = Client.objects.filter(star_flag=True).order_by('client_name')
    members = Member.objects.all().order_by('user__first_name')

    context = {
        'title': 'Flagged Accounts',
        'accounts': accounts,
        'members': members
    }

    return render(request, 'reports/flagged_accounts_refactor.html', context)


@login_required
def performance_anomalies(request):
    """
    Finds campaigns that are underperforming or overperforming
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    accounts = Client.objects.filter(Q(target_cpa__gt=0.0) | Q(target_roas__gt=0.0)).order_by('client_name')

    excellent_accounts = []
    good_accounts = []
    fair_accounts = []
    bad_accounts = []

    for account in accounts:
        if account.target_roas > 0.0:
            roas_diff = (account.roas_this_month - account.target_roas) / account.target_roas
            if roas_diff >= 0.1:
                excellent_accounts.append(account)
            elif roas_diff >= 0.0:
                good_accounts.append(account)
            elif roas_diff >= -0.1:
                fair_accounts.append(account)
            elif roas_diff < -0.1:
                bad_accounts.append(account)

        if account.target_cpa > 0.0:
            cpa_diff = (account.cpa_this_month - account.target_cpa) / account.target_cpa
            if cpa_diff >= 0.1:
                excellent_accounts.append(account)
            elif cpa_diff >= 0.0:
                good_accounts.append(account)
            elif cpa_diff >= -0.1:
                fair_accounts.append(account)
            elif cpa_diff < -0.1:
                bad_accounts.append(account)

    context = {
        'title': 'Performance Anomalies',
        'excellent_accounts': excellent_accounts,
        'good_accounts': good_accounts,
        'fair_accounts': fair_accounts,
        'bad_accounts': bad_accounts
    }

    return render(request, 'reports/performance_anomalies_refactor.html', context)


@login_required
def account_history(request):
    """
    The overall monthly account reports
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    default_month = now.month
    default_year = now.year

    months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    years = [str(i) for i in range(2018, now.year + 1)]

    selected = {
        'account': 'all',
        'month': 'all',
        'year': now.year
    }

    # TODO fix
    month = default_month
    year = default_year

    all_accounts = Client.objects.all().order_by('client_name')
    accounts = all_accounts
    accounts_array = []

    if request.method == 'POST':
        if request.POST.get('year') != 'all':
            year = int(request.POST.get('year'))
            selected['year'] = year
        if request.POST.get('month') != 'all':
            month = int(request.POST.get('month'))
            selected['month'] = month
        if request.POST.get('account') != 'all':
            accounts = all_accounts.filter(id=request.POST.get('account'))
            selected['account'] = accounts[0].id

    for account in accounts:
        try:
            bh = AccountBudgetSpendHistory.objects.get(month=month, year=year, account=account)
        except AccountBudgetSpendHistory.DoesNotExist:
            continue

        allocated_history = AccountAllocatedHoursHistory.objects.filter(month=month, year=year, account=account).values(
            'account', 'year', 'month').annotate(sum_hours=Sum('allocated_hours'))
        allocated_hours = 0.0
        if allocated_history.count() > 0 and 'sum_hours' in allocated_history[0]:
            allocated_hours = allocated_history[0]['sum_hours']

        all_hours = account.all_hours_month_year(month, year)
        try:
            actual_hours_ratio = all_hours / allocated_hours
        except ZeroDivisionError:
            actual_hours_ratio = 'N/A'

        value_added_hours = account.value_hours_month_year(month, year)
        mandate_hours = account.actual_mandate_hours(month, year)
        actual_hours_sum = account.actual_hours_month_year(month, year)

        tmpa = []
        tmpa.append(account)  # 0
        tmpa.append(bh)  # 1
        tmpa.append(allocated_hours)  # 2
        tmpa.append(all_hours)  # 3
        tmpa.append(actual_hours_ratio)  # 4
        tmpa.append(value_added_hours)  # 5
        tmpa.append(mandate_hours)  # 6
        tmpa.append(actual_hours_sum)  # 7
        accounts_array.append(tmpa)

    context = {
        'title': 'Account History',
        'months': months,
        'years': years,
        'all_accounts': all_accounts,
        'accounts_array': accounts_array
    }

    return render(request, 'reports/account_history_refactor.html', context)


@login_required
def tier_overview(request):
    """
    Tier overview
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    proposals = TierChangeProposal.objects.filter(changed_by=None)
    changed_proposals = TierChangeProposal.objects.exclude(changed_by=None)

    context = {
        'title': 'Tier Overview',
        'proposals': proposals,
        'changed_proposals': changed_proposals
    }

    return render(request, 'reports/tier_center.html', context)


@login_required
def update_tier(request):
    """
    Updates an account's tier from a tier proposal
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    proposal_id = request.POST.get('proposal_id')
    accept_change = int(request.POST.get('accept')) == 1
    proposal = TierChangeProposal.objects.get(id=proposal_id)

    """
    Execute proposal
    """
    if accept_change:
        proposal.account.tier = proposal.tier_to
        proposal.changed = True
    else:
        proposal.changed = False
    proposal.changed_by = Member.objects.get(user=request.user)
    proposal.save()

    return HttpResponse('Success')


@login_required
def outstanding_notifications(request):
    """
    Report to show who hasn't acknowledged their notifications
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    outstanding = Notification.objects.filter(confirmed=False).order_by('created')

    context = {
        'title': 'Outstanding Notifications',
        'rnotifications': outstanding
    }

    return render(request, 'reports/outstanding_notifications_refactor.html', context)


@login_required
def high_fives(request):
    """
    High five reports page
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    high_fives = HighFive.objects.all()

    context = {
        'title': 'High Fives',
        'high_fives': high_fives
    }

    return render(request, 'reports/high_fives_refactor.html', context)


@login_required
def new_high_five(request):
    """
    New high five page
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'GET':
        members = Member.objects.all().order_by('user__first_name')

        context = {
            'title': 'New High Five',
            'members': members
        }

        return render(request, 'reports/new_high_five_refactor.html', context)
    elif request.method == 'POST':
        r = request.POST
        high_five = HighFive()

        date_text = r.get('hf-date')
        try:
            high_five.date = datetime.datetime.strptime(date_text, '%m/%d/%Y')
        except ValueError:  # if invalid date format given, get current date
            high_five.date = datetime.datetime.today().strftime('%Y-%m-%d')

        high_five.nominator = Member.objects.get(id=r.get('nominator'))
        high_five.member = Member.objects.get(id=r.get('member'))
        high_five.description = r.get('description')
        high_five.save()

        # create todo for member
        description = 'You\'ve received a new high five! Head over to the performance tab to view it.'
        link = '/user_management/members/' + str(high_five.member.id) + '/performance'
        Todo.objects.create(member=high_five.member, description=description, link=link, type=5)

        mail_details = {
            'hf': high_five
        }

        msg_html = render_to_string(TEMPLATE_DIR + '/mails/new_high_five.html', mail_details)

        send_mail(
            'New High Five Created', msg_html,
            EMAIL_HOST_USER, settings.OOPS_HF_MAILING_LIST, fail_silently=False, html_message=msg_html)

        return redirect('/reports/high_fives')


@login_required
def incidents(request):
    """
    Incidents page
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    client_oops = Incident.objects.all()
    internal_oops = InternalOops.objects.all()

    context = {
        'title': 'Oops',
        'client_oops': client_oops,
        'internal_oops': internal_oops
    }

    return render(request, 'reports/oops_refactor.html', context)


@login_required
def new_internal_oops(request):
    """
    New internal oops page
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'GET':
        members = Member.objects.exclude(deactivated=True).order_by('user__first_name')
        issue_types = IncidentReason.objects.all()

        context = {
            'title': 'New Internal Oops',
            'members': members,
            'issue_types': issue_types
        }

        return render(request, 'reports/new_internal_oops.html', context)
    elif request.method == 'POST':
        reporter_id = request.POST.get('reporting_member')
        try:
            reporter = Member.objects.get(id=reporter_id)
        except Member.DoesNotExist:
            return HttpResponseNotFound('The reporting member does not exist!')
        date = request.POST.get('incident_date')
        try:
            date = datetime.datetime.strptime(date, '%m/%d/%Y')
        except ValueError:
            return HttpResponse('Invalid date format! Please use the datepicker.')
        members = []
        for member_id in request.POST.getlist('members'):
            try:
                members.append(Member.objects.get(id=member_id))
            except Member.DoesNotExist:
                return HttpResponseNotFound('One of the responsible members does not exist!')
        issue_type = request.POST.get('issue_type')
        if issue_type is not None:
            try:
                issue_type = IncidentReason.objects.get(id=issue_type)
            except IncidentReason.DoesNotExist:
                return HttpResponseNotFound('The issue type does not exist!')
        description = request.POST.get('issue_description')

        internal_oops = InternalOops()
        internal_oops.reporter = reporter
        internal_oops.date = date
        internal_oops.save()
        internal_oops.members.set(members)
        internal_oops.issue = issue_type
        internal_oops.description = description
        internal_oops.save()

        internal_oops.save()

        # send email to mailing list
        mail_details = {
            'incident': internal_oops
        }

        msg_html = render_to_string(TEMPLATE_DIR + '/mails/new_internal_oops.html', mail_details)

        send_mail(
            'New Internal Oops Report Created', msg_html,
            EMAIL_HOST_USER, settings.OOPS_HF_MAILING_LIST, fail_silently=False, html_message=msg_html)

        return redirect('/reports/oops')


@login_required
def new_client_oops(request):
    """
    New client page
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    if request.method == 'GET':
        accounts = Client.objects.all().order_by('client_name')
        members = Member.objects.exclude(deactivated=True).order_by('user__first_name')
        platforms = Incident.PLATFORMS
        services = Incident.SERVICES
        issue_types = IncidentReason.objects.all()

        context = {
            'title': 'New Client Oops',
            'accounts': accounts,
            'members': members,
            'platforms': platforms,
            'services': services,
            'issue_types': issue_types
        }

        return render(request, 'reports/new_client_oops.html', context)
    elif request.method == 'POST':
        r = request.POST
        # get form data
        try:
            reporter_id = int(r.get('reporting_member'))
        except ValueError:
            reporter_id = 0
        try:
            service = int(r.get('services'))
        except ValueError:
            service = 6  # set to None by default
        try:
            account = int(r.get('account'))
        except ValueError:
            account = 0
        date = r.get('incident_date')
        description = r.get('issue_description')
        try:
            issue_type = int(r.get('issue_type'))
        except (ValueError, TypeError):
            issue_type = None
        try:
            budget_error_amt = float(r.get('budget_error'))
        except (ValueError, TypeError):
            budget_error_amt = 0.0
        try:
            platform = r.get('platform')
        except ValueError:
            platform = 3  # set to other by default

        client_aware = r.get('client_aware') == '1'
        client_at_risk = r.get('client_at_risk') == '1'
        members_addressed = r.get('members_addressed') == '1'
        justification = r.get('justification')

        # create incident
        incident = Incident()
        incident.timestamp = datetime.datetime.now()
        incident.reporter = Member.objects.get(id=reporter_id)
        incident.service = service
        incident.account = Client.objects.get(id=account)
        try:
            incident.date = datetime.datetime.strptime(date, '%m/%d/%Y')
        except ValueError:  # if invalid date format given, get current date
            incident.date = datetime.datetime.today().strftime('%Y-%m-%d')
        incident.save()

        members = []
        for member_id in r.getlist('member'):
            try:
                members.append(Member.objects.get(id=member_id))
            except Member.DoesNotExist:
                pass
        incident.members.set(members)

        incident.description = description
        if issue_type is not None:
            try:
                incident_reason = IncidentReason.objects.get(id=issue_type)
            except IncidentReason.DoesNotExist:
                incident_reason = None
        else:
            incident_reason = None

        incident.issue = incident_reason
        incident.budget_error_amount = budget_error_amt
        incident.platform = platform
        incident.client_aware = client_aware
        incident.client_at_risk = client_at_risk
        incident.addressed_with_member = members_addressed
        incident.justification = justification

        try:
            refund_amount = float(r.get('refund_amount'))
            incident.refund_amount = refund_amount
        except (ValueError, TypeError):
            pass

        incident.save()

        # send email to mailing list
        mail_details = {
            'incident': incident
        }

        msg_html = render_to_string(TEMPLATE_DIR + '/mails/new_incident.html', mail_details)

        send_mail(
            'New Client Oops Report Created', msg_html,
            EMAIL_HOST_USER, settings.OOPS_HF_MAILING_LIST, fail_silently=False, html_message=msg_html)

        return redirect('/reports/oops')


@login_required
def onboarding(request):
    """
    Onboarding report
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    onboarding_accounts = Client.objects.filter(status=0).order_by('client_name')

    context = {
        'title': 'Onboarding Accounts',
        'onboarding_accounts': onboarding_accounts
    }

    return render(request, 'reports/onboarding_refactor.html', context)


@login_required
def sales(request):
    """
    Sales report
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    opportunities = Opportunity.objects.filter(addressed=False)

    context = {
        'title': 'Sales',
        'opportunities': opportunities
    }

    return render(request, 'reports/sales_refactor.html', context)


@login_required
def jamie(request):
    """
    Jamie's custom report
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    roles = Role.objects.filter(Q(name='AM') | Q(name='Account Coordinator') | Q(name='Account Manager'))
    ams = Member.objects.filter(role__in=roles).order_by('user__first_name')
    status_badges = ['info', 'success', 'warning', 'danger']

    context = {
        'title': 'Jamie',
        'ams': ams,
        'status_badges': status_badges
    }

    return render(request, 'reports/jamie.html', context)


@login_required
def promo_ads(request):
    """
    Jamie's custom report
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    # Change this later
    bad_ad_alerts = BadAdAlert.objects.all()

    context = {
        'title': 'Promo Ads',
        'bad_ad_alerts': bad_ad_alerts
    }

    return render(request, 'reports/promo_ads_refactor.html', context)


@login_required
def over_under(request):
    """
    Over/under report
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    first = now.replace(day=1)
    # Default to last month
    last_month = first - datetime.timedelta(days=1)

    months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    years = [str(i) for i in range(2018, now.year + 1)]

    month = request.GET.get('month') if 'month' in request.GET else last_month.month
    year = request.GET.get('year') if 'year' in request.GET else last_month.year

    selected = {
        'month': str(month),
        'year': str(year)
    }

    all_accounts = Client.objects.all().order_by('client_name')

    # Contain the accounts that overspent hours or underspend hours
    overspenders = []
    underspenders = []

    for account in all_accounts:
        allocated_history = AccountAllocatedHoursHistory.objects.filter(month=month, year=year, account=account).values(
            'account', 'year', 'month').annotate(sum_hours=Sum('allocated_hours'))
        allocated_hours = 0.0
        if allocated_history.count() > 0 and 'sum_hours' in allocated_history[0]:
            allocated_hours = allocated_history[0]['sum_hours']

        all_hours = account.all_hours_month_year(month, year)

        if allocated_hours == 0:
            continue

        try:
            actual_hours_ratio = all_hours / allocated_hours
        except ZeroDivisionError:
            actual_hours_ratio = 0.0

        tmpa = []
        tmpa.append(account)
        tmpa.append(allocated_hours)
        tmpa.append(all_hours)
        tmpa.append(actual_hours_ratio)

        if float(actual_hours_ratio) >= 1.2:
            overspenders.append(tmpa)
        elif float(actual_hours_ratio) <= 0.8:
            underspenders.append(tmpa)

        # value_added_hours = account.value_hours_month_year(month, year)
        # mandate_hours = account.actual_mandate_hours(month, year)
        # actual_hours_sum = account.actual_hours_month_year(month, year)
        #
        # tmpa = []
        # tmpa.append(account)  # 0
        # tmpa.append(bh)  # 1
        # tmpa.append(allocated_hours)  # 2
        # tmpa.append(all_hours)  # 3
        # tmpa.append(actual_hours_ratio)  # 4
        # tmpa.append(value_added_hours)  # 5
        # tmpa.append(mandate_hours)  # 6
        # tmpa.append(actual_hours_sum)  # 7
        # accounts_array.append(tmpa)

    context = {
        'title': 'Over Under Report',
        'months': months,
        'years': years,
        'selected': selected,
        'overspenders': overspenders,
        'underspenders': underspenders
    }

    return render(request, 'reports/over_under_refactor.html', context)


@login_required
def month_over_month(request):
    """
    Month over month report
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.datetime.now()
    first = now.replace(day=1)
    # Default to last month
    last_month = first - datetime.timedelta(days=1)

    month = int(request.GET.get('month')) if 'month' in request.GET else last_month.month
    year = int(request.GET.get('year')) if 'year' in request.GET else last_month.year
    account_id = int(request.GET.get('account_id')) if 'account_id' in request.GET else None
    accounts = Client.objects.all()

    try:
        account = accounts.get(id=account_id) if account_id is not None else None
    except Client.DoesNotExist:
        account = None

    selected = {
        'month': str(month),
        'year': str(year),
        'account_id': account_id
    }

    month_strs = []
    cur_month = month
    cur_year = year

    # Prepare the report
    report = []

    for i in range(10):
        month_strs.insert(0, str(calendar.month_name[cur_month]) + ', ' + str(cur_year))
        if account is not None:
            tmpd = {}
            try:
                bh = AccountBudgetSpendHistory.objects.get(month=cur_month, year=cur_year, account=account)
                tmpd['fee'] = round(bh.management_fee, 2)
                tmpd['spend'] = round(bh.spend, 2)
                tmpd['aw_spend'] = round(bh.aw_spend, 2)
                tmpd['fb_spend'] = round(bh.fb_spend, 2)
                tmpd['bing_spend'] = round(bh.bing_spend, 2)
            except AccountBudgetSpendHistory.DoesNotExist:
                tmpd['fee'] = 0.0
                tmpd['spend'] = 0.0

            tmpd['actual'] = account.all_hours_month_year(cur_month, cur_year)
            allocated_history = AccountAllocatedHoursHistory.objects.filter(month=cur_month, year=cur_year,
                                                                            account=account).values('account', 'year',
                                                                                                    'month').annotate(
                sum_hours=Sum('allocated_hours'))
            allocated_hours = 0.0
            if allocated_history.count() > 0 and 'sum_hours' in allocated_history[0]:
                allocated_hours = allocated_history[0]['sum_hours']

            tmpd['allocated'] = allocated_hours
            try:
                tmpd['ratio'] = tmpd['actual'] / tmpd['allocated']
            except ZeroDivisionError:
                tmpd['ratio'] = 0.0

            report.insert(0, tmpd)

        cur_month -= 1
        if cur_month == 0:
            cur_month = 12
            cur_year -= 1

    context = {
        'title': 'Month Over Month Report',
        'accounts': accounts,
        'account': account,
        'selected': selected,
        'month_strs': month_strs,
        'report': report
    }

    return render(request, 'reports/month_over_month.html', context)


@login_required
def tag_report(request):
    """
    Let's tags be queried and filtered
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to view this page')

    tags = Tag.objects.all()

    if 'tag' in request.GET:
        try:
            tag = tags.get(id=request.GET.get('tag'))
        except Tag.DoesNotExist:
            return HttpResponseNotFound('No tag with that ID')
        accounts = tag.client_set.all()
    else:
        tag = None
        accounts = []

    context = {
        'title': 'Tags',
        'tags': tags,
        'tag': tag,
        'accounts': accounts
    }

    return render(request, 'reports/tags_refactor.html', context)
