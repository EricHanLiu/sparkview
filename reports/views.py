from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from user_management.models import Member, Team, Incident, Role
from client_area.models import AccountHourRecord, Promo
from budget.models import Client
import datetime

# Create your views here.
@login_required
def agency_overview(request):
    if (not request.user.is_staff):
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
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')
    accounts = Client.objects.filter(status=1)

    total_projected_loss = 0.0
    total_projected_overspend = 0.0
    for account in accounts:
        total_projected_loss += account.projected_loss
        if (account.projected_loss < 0): # we will overspend
            total_projected_overspend += self.project_yesterday - self.current_budget

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
    if (not request.user.is_staff):
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
    if (not request.user.is_staff):
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
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    # Probably has to be changed before production
    role = Role.objects.filter(Q(name='SEO') | Q(name='SEO Analyst') | Q(name='SEO Intern'))
    members = Member.objects.filter(role__in=role)

    actual_aggregate = 0.0
    allocated_aggregate = 0.0
    available_aggregate = 0.0

    seo_accounts = Client.objects.filter(Q(has_seo=True) | Q(has_cro=True)).filter(Q(status=0) | Q(status=1))

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

    report_type = 'SEO Member Capacity Report'

    context = {
        'members' : members,
        'actual_aggregate' : actual_aggregate,
        'capacity_rate' : capacity_rate,
        'utilization_rate': utilization_rate,
        'allocated_aggregate' : allocated_aggregate,
        'available_aggregate' : available_aggregate,
        'report_type' : report_type,
        'seo_accounts' : seo_accounts
    }

    return render(request, 'reports/seo_member_capacity_report.html', context)

@login_required
def strat_capacity(request):
        """
        Creates report that shows the capacity of the strats on an aggregated and individual basis
        """
        if (not request.user.is_staff):
            return HttpResponse('You do not have permission to view this page')

        # Probably has to be changed before production
        role = Role.objects.filter(Q(name='	Strategist'))
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
    if (not request.user.is_staff):
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
    if (not request.user.is_staff):
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
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    promos = Promo.objects.filter(end_date__gte=datetime.datetime.now())

    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(1)
    today_start = datetime.datetime.combine(today, datetime.time())
    today_end = datetime.datetime.combine(tomorrow, datetime.time())

    promos_start_today = Promo.objects.filter(start_date__gte=today_start, start_date__lte=today_end)
    promos_end_today = Promo.objects.filter(end_date__gte=today_start, end_date__lte=today_end)

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
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    if (request.method == 'GET'):
        now = datetime.datetime.now()
        hours = AccountHourRecord.objects.filter(year=now.year, month=now.month, is_unpaid=False).annotate(Sum('hours'))
    elif (request.method == 'POST'):
        pass
    else:
        return HttpResponse('Invalid request type')

    context = {
        'hours' : hours
    }

    return render(request, 'reports/actual_hours.html', context)
