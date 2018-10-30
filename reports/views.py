from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from user_management.models import Member, Team, Incident, Role
from client_area.models import AccountHourRecord
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
    for account in accounts:
        total_projected_loss += account.projected_loss

    context = {
        'accounts' : accounts,
        'total_projected_loss' : total_projected_loss
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

    report_type = 'Paid Media Member Capacity Report'

    context = {
        'members' : members,
        'actual_aggregate' : actual_aggregate,
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

    report_type = 'AM Member Capacity Report'

    context = {
        'members' : members,
        'actual_aggregate' : actual_aggregate,
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

    for member in members:
        actual_aggregate += member.actualHoursThisMonth
        allocated_aggregate += member.allocated_hours_month()
        available_aggregate += member.hours_available

    report_type = 'SEO Member Capacity Report'

    context = {
        'members' : members,
        'actual_aggregate' : actual_aggregate,
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
