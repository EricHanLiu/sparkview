from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from user_management.models import Member, Team, Incident, Role
from client_area.models import AccountAllocatedHoursHistory, AccountHourRecord, Promo, MonthlyReport
from budget.models import Client, AccountBudgetSpendHistory, TierChangeProposal
from notifications.models import Notification
import datetime, calendar

# Create your views here.
@login_required
def agency_overview(request):
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    # Get account related metrics
    total_active_accounts = Client.objects.filter(status=1)
    total_active_seo = Client.objects.filter(status=1).filter(has_seo=True).count()
    total_active_cro = Client.objects.filter(status=1).filter(has_cro=True).count()

    total_onboarding = Client.objects.filter(status=0).count()
    total_inactive = Client.objects.filter(status=2).count()
    total_lost = Client.objects.filter(status=3).count()

    incident_count = Incident.objects.all().count()

    # Members
    members = Member.objects.all()

    sorted_members_by_count = sorted(members, key=lambda t: t.incidents)

    # Total management fee
    # total_management_fee = 0.0
    total_allocated_hours = 0.0

    for aa in total_active_accounts:
        # total_management_fee += aa.totalFee
        total_allocated_hours += aa.allHours

    # hours worked this month
    now   = datetime.datetime.now()
    month = now.month
    year  = now.year
    total_hours_worked = AccountHourRecord.objects.filter(month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
    if (total_hours_worked == None):
        total_hours_worked = 0.0

    allocation_ratio = total_hours_worked / total_allocated_hours

    context = {
        'total_active_accounts' : total_active_accounts.count(),
        'total_active_seo' : total_active_seo,
        'total_active_cro' : total_active_cro,
        'total_onboarding' : total_onboarding,
        'total_inactive': total_inactive,
        'total_lost': total_lost,
        # 'total_fee' : total_management_fee,
        'incident_count': incident_count,
        'top_offenders': sorted_members_by_count,
        'allocation_ratio' : allocation_ratio,
        'total_allocated_hours' : total_allocated_hours,
        'total_hours_worked' : total_hours_worked
    }

    return render(request, 'reports/agency_overview.html', context)


@login_required
def account_spend_progression(request):
    """
    Creates the report that warns about accounts that may lose values
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')
    accounts = Client.objects.filter(status=1)

    total_projected_loss = 0.0
    total_projected_overspend = 0.0
    for account in accounts:
        total_projected_loss += account.projected_loss
        if (account.projected_loss < 0): # we will overspend
            total_projected_overspend += account.project_yesterday - account.current_budget

    context = {
        'accounts' : accounts,
        'total_projected_loss' : total_projected_loss,
        'total_projected_overspend' : total_projected_overspend
    }

    return render(request, 'reports/account_spend_progression.html', context)


@login_required
def cm_capacity(request):
    """
    Creates report that shows the capacity of the PPC campaign managers on an aggregated and individual basis
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    # Probably has to be changed before production
    # This badly has to be fixed when we implement proper roles
    # TODO: Make this reasonable
    role = Role.objects.filter(Q(name='CM') | Q(name='PPC Specialist') | Q(name='PPC Analyst') | Q(name='PPC Intern') | Q(name='PPC Team Lead'))
    members = Member.objects.filter(role__in=role)

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0

    for member in members:
        actual_aggregate += member.actualHoursThisMonth
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

    report_type = 'Paid Media Member Capacity Report'

    context = {
        'members' : members,
        'actual_aggregate' : actual_aggregate,
        'capacity_rate' : capacity_rate,
        'utilization_rate': utilization_rate,
        'allocated_aggregate' : allocated_aggregate,
        'available_aggregate' : available_aggregate,
        'report_type' : report_type
    }

    return render(request, 'reports/member_capacity_report.html', context)


@login_required
def am_capacity(request):
    """
    Creates report that shows the capacity of the account managers on an aggregated and individual basis
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    # Probably has to be changed before production
    role = Role.objects.filter(Q(name='AM') | Q(name='Account Coordinator') | Q(name='Account Manager'))
    members = Member.objects.filter(role__in=role)

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0

    for member in members:
        actual_aggregate += member.actualHoursThisMonth
        allocated_aggregate += member.allocated_hours_month()
        available_aggregate += member.hours_available

    if allocated_aggregate + available_aggregate == 0:
        capacity_rate = 0
    else:
        capacity_rate = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

    if (allocated_aggregate == 0):
        utilization_rate = 0
    else:
        utilization_rate = 100 * (actual_aggregate / allocated_aggregate)


    report_type = 'AM Member Capacity Report'

    context = {
        'members' : members,
        'actual_aggregate' : actual_aggregate,
        'capacity_rate' : capacity_rate,
        'utilization_rate': utilization_rate,
        'allocated_aggregate' : allocated_aggregate,
        'available_aggregate' : available_aggregate,
        'report_type' : report_type
    }

    return render(request, 'reports/member_capacity_report.html', context)


@login_required
def seo_capacity(request):
    """
    Creates report that shows the capacity of the account managers on an aggregated and individual basis
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    # Probably has to be changed before production
    role = Role.objects.filter(Q(name='SEO') | Q(name='SEO Analyst') | Q(name='SEO Intern'))
    members = Member.objects.filter(role__in=role)

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0

    total_seo_hours = 0.0
    total_cro_hours = 0.0

    statusBadges = ['info', 'success', 'warning', 'danger']
    seo_accounts = Client.objects.filter(Q(has_seo=True) | Q(has_cro=True)).filter(Q(status=0) | Q(status=1))

    for member in members:
        actual_aggregate += member.actualHoursThisMonth
        allocated_aggregate += member.allocated_hours_month()
        available_aggregate += member.hours_available

    for account in seo_accounts:
        if account.has_seo:
            total_seo_hours += account.seo_hours
        if account.has_cro:
            total_cro_hours += account.cro_hours

    if allocated_aggregate + available_aggregate == 0:
        capacity_rate = 0
    else:
        capacity_rate = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

    if (allocated_aggregate == 0):
        utilization_rate = 0
    else:
        utilization_rate = 100 * (actual_aggregate / allocated_aggregate)

    report_type = 'SEO Member Capacity Report'

    context = {
        'members' : members,
        'actual_aggregate' : actual_aggregate,
        'capacity_rate' : capacity_rate,
        'utilization_rate': utilization_rate,
        'allocated_aggregate' : allocated_aggregate,
        'available_aggregate' : available_aggregate,
        'report_type' : report_type,
        'seo_accounts' : seo_accounts,
        'statusBadges' : statusBadges,
        'total_seo_hours' : total_seo_hours,
        'total_cro_hours' : total_cro_hours
    }

    return render(request, 'reports/seo_member_capacity_report.html', context)


@login_required
def strat_capacity(request):
        """
        Creates report that shows the capacity of the strats on an aggregated and individual basis
        """
        if not request.user.is_staff:
            return HttpResponse('You do not have permission to view this page')

        # Probably has to be changed before production
        role = Role.objects.filter(Q(name='Strategist'))
        members = Member.objects.filter(role__in=role)

        actual_aggregate = 0.0
        allocated_aggregate = 0.0
        available_aggregate = 0.0

        for member in members:
            actual_aggregate += member.actualHoursThisMonth
            allocated_aggregate += member.allocated_hours_month()
            available_aggregate += member.hours_available

        if allocated_aggregate + available_aggregate == 0:
            capacity_rate = 0
        else:
            capacity_rate = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

        if (allocated_aggregate == 0):
            utilization_rate = 0
        else:
            utilization_rate = 100 * (actual_aggregate / allocated_aggregate)

        report_type = 'Strategy Capacity Report'

        context = {
            'members' : members,
            'actual_aggregate' : actual_aggregate,
            'capacity_rate' : capacity_rate,
            'utilization_rate': utilization_rate,
            'allocated_aggregate' : allocated_aggregate,
            'available_aggregate' : available_aggregate,
            'report_type' : report_type
        }

        return render(request, 'reports/member_capacity_report.html', context)


@login_required
def hour_log(request):
    """
    Creates report that shows which users have added hours this month
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    now   = datetime.datetime.now()
    month = now.month
    year  = now.year

    members = Member.objects.all()

    context = {
        'members':members
    }

    return render(request, 'reports/hour_log.html', context)


@login_required
def facebook(request):
    """
    Creates report that just shows active FB accounts
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.exclude(facebook=None).filter(status=1)

    context = {
        'accounts' : accounts
    }

    return render(request, 'reports/facebook.html', context)


@login_required
def promos(request):
    """
    Shows calendar of all going on and upcoming promos
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    seven_days_ago = datetime.datetime.now() - datetime.timedelta(7)
    seven_days_future = datetime.datetime.now() + datetime.timedelta(7)
    promos = Promo.objects.filter(end_date__gte=seven_days_ago)

    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(1)
    today_start = datetime.datetime.combine(today, datetime.time())
    today_end = datetime.datetime.combine(tomorrow, datetime.time())

    promos_start_today = Promo.objects.filter(start_date__gte=today_start, start_date__lte=seven_days_future) #this is really this week
    promos_end_today = Promo.objects.filter(end_date__gte=today_start, end_date__lte=seven_days_future)

    context = {
        'promos' : promos,
        'promos_start_today' : promos_start_today,
        'promos_end_today' : promos_end_today
    }

    return render(request, 'reports/promos.html', context)


@login_required
def actual_hours(request):
    """
    Shows tables of all hours from selection of members, clients, and month
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    now = datetime.datetime.now()
    accounts = Client.objects.all()
    members = Member.objects.all()
    months = [(str(i), calendar.month_name[i]) for i in range(1,13)]
    years = ['2018', '2019', '2020']

    selected = {}
    selected['account'] = 'all'
    selected['member'] = 'all'
    selected['month'] = 'all'
    selected['year'] = now.year

    if (request.method == 'GET'):
        hours = AccountHourRecord.objects.filter(year=now.year, month=now.month, is_unpaid=False).values('member', 'account', 'year', 'month').annotate(sum_hours=Sum('hours'))
    elif (request.method == 'POST'):
        year = request.POST.get('year')
        month = request.POST.get('month')
        member = request.POST.get('member')
        account = request.POST.get('account')

        hours = AccountHourRecord.objects.filter()

        if (year != 'all'):
            hours = hours.filter(year=year)
            selected['year'] = year
        if (month != 'all'):
            hours = hours.filter(month=month)
            selected['month'] = month
        if (member != 'all'):
            hours = hours.filter(member=member)
            selected['member'] = int(member)
        if (account != 'all'):
            hours = hours.filter(account=account)
            selected['account'] = int(account)

        hours = hours.values('member', 'account', 'year', 'month').annotate(sum_hours=Sum('hours'))

    else:
        return HttpResponse('Invalid request type')

    for hour in hours:
        hour['member'] = members.get(id=hour['member'])
        hour['account'] = accounts.get(id=hour['account'])

    context = {
        'hours' : hours,
        'accounts' : accounts,
        'members' : members,
        'months' : months,
        'years' : years,
        'selected' : selected
    }

    return render(request, 'reports/actual_hours.html', context)


@login_required
def monthly_reporting(request):
    """
    Shows status of reports
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    now = datetime.datetime.now()
    accounts = Client.objects.all()
    teams = Team.objects.all()
    months = [(str(i), calendar.month_name[i]) for i in range(1,13)]
    years = ['2018', '2019', '2020']

    selected = {}
    selected['account'] = 'all'
    selected['month'] = 'all'
    selected['year'] = now.year
    selected['team'] = 'all'

    if (request.method == 'GET'):
        reports = MonthlyReport.objects.filter(year=now.year, month=now.month)
    elif (request.method == 'POST'):
        year = request.POST.get('year')
        month = request.POST.get('month')
        account_id = request.POST.get('account')
        team_id = request.POST.get('team')

        reports = MonthlyReport.objects.filter()

        if (year != 'all'):
            reports = reports.filter(year=year)
            selected['year'] = year
        if (month != 'all'):
            reports = reports.filter(month=month)
            selected['month'] = month
        if (team_id != 'all'):
            team = Team.objects.get(id=team_id)
            team_accounts = accounts.filter(team=team)
            reports = reports.filter(account__in=team_accounts)
            selected['team'] = int(team_id)
        if (account_id != 'all'):
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
        'reports' : reports,
        'accounts' : accounts,
        'ontime_pct' : ontime_rate,
        'completion_pct' : completion_rate,
        'teams' : teams,
        'months' : months,
        'years' : years,
        'selected' : selected
    }

    return render(request, 'reports/monthly_reports.html', context)


@login_required
def account_capacity(request):
    """
    Capacity report for accounts
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.filter(status=1) # active accounts only

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0

    for account in accounts:
        actual_aggregate += account.hoursWorkedThisMonth
        allocated_aggregate += account.allHours
        # available_aggregate += member.hours_available

    # if allocated_aggregate + available_aggregate == 0:
    #     capacity_rate = 0
    # else:
    #     capacity_rate = 100 * (allocated_aggregate / (allocated_aggregate + available_aggregate))

    if (allocated_aggregate == 0):
        utilization_rate = 0
    else:
        utilization_rate = 100 * (actual_aggregate / allocated_aggregate)


    report_type = 'Account Capacity Report'

    context = {
        'accounts' : accounts,
        'actual_aggregate' : actual_aggregate,
        # 'capacity_rate' : capacity_rate,
        'utilization_rate': utilization_rate,
        'allocated_aggregate' : allocated_aggregate,
        # 'available_aggregate' : available_aggregate,
        'report_type' : report_type
    }

    return render(request, 'reports/account_capacity_report.html', context)


@login_required
def backup_report(request):
    """
    Lists accounts that currently have backups
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.exclude(cmb=None, amb=None, seob=None, stratb=None)

    context = {
        'accounts' : accounts
    }

    return render(request, 'reports/backup_report.html', context)


@login_required
def flagged_accounts(request):
    """
    Lists accounts that currently have backups
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.filter(star_flag=True)
    members = Member.objects.all()

    context = {
        'accounts' : accounts,
        'members': members
    }

    return render(request, 'reports/flagged_accounts.html', context)


@login_required
def performance_anomalies(request):
    """
    Finds campaigns that are underperforming or overperforming
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    accounts = Client.objects.filter(Q(target_cpa__gt=0.0) | Q(target_roas__gt=0.0))

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
        'excellent_accounts' : excellent_accounts,
        'good_accounts' : good_accounts,
        'fair_accounts' : fair_accounts,
        'bad_accounts' : bad_accounts
    }

    return render(request, 'reports/performance_anomalies.html', context)


@login_required
def account_history(request):
    """
    The overall monthly account reports
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    now = datetime.datetime.now()
    default_month = now.month
    default_year = now.year

    months = [(str(i), calendar.month_name[i]) for i in range(1,13)]
    years = ['2018', '2019', '2020']

    selected = {}
    selected['account'] = 'all'
    selected['month'] = 'all'
    selected['year'] = now.year

    # TODO fix
    month = default_month
    year = default_year

    all_accounts = Client.objects.all()
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
        except:
            continue

        allocated_history = AccountAllocatedHoursHistory.objects.filter(month=month, year=year, account=account).values('account', 'year', 'month').annotate(sum_hours=Sum('allocated_hours'))
        allocated_hours = 0.0
        if allocated_history.count() > 0 and 'sum_hours' in allocated_history[0]:
            allocated_hours = allocated_history[0]['sum_hours']

        actual_hours = account.actual_hours_month_year(month, year)
        try:
            actual_hours_ratio = actual_hours / allocated_hours
        except:
            actual_hours_ratio = 'N/A'

        tmpa = []
        tmpa.append(account) #0
        tmpa.append(bh) #1
        tmpa.append(allocated_hours) #2
        tmpa.append(actual_hours) #3
        tmpa.append(actual_hours_ratio) #4
        accounts_array.append(tmpa)

    context = {
        'months' : months,
        'years' : years,
        'all_accounts' : all_accounts,
        'accounts_array' : accounts_array
    }

    return render(request, 'reports/account_history.html', context)

@login_required
def tier_overview(request):
    """
    Tier overview
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    proposals = TierChangeProposal.objects.filter(changed_by=None)
    changed_proposals = TierChangeProposal.objects.exclude(changed_by=None)

    context = {
        'proposals' : proposals,
        'changed_proposals' : changed_proposals
    }

    return render(request, 'reports/tier_center.html', context)


@login_required
def update_tier(request):
    """
    Updates an account's tier from a tier proposal
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

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
        return HttpResponse('You do not have permission to view this page')

    outstanding = Notification.objects.filter(confirmed=False).order_by('created')

    context = {
        'rnotifications' : outstanding
    }

    return render(request, 'reports/outstanding_notifications.html', context)

@login_required
def incidents(request):
    """
    Incidents page
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    return render(request, 'reports/incidents.html')

@login_required
def new_incident(request):
    """
    New incident page
    """
    if not request.user.is_staff:
        return HttpResponse('You do not have permission to view this page')

    

    return render(request, 'reports/new_incident.html')
