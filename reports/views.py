from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from user_management.models import Member, Team
from client_area.models import AccountHourRecord
from budget.models import Client
import datetime

# Create your views here.
def agency_overview(request):
    if (not request.user.is_staff):
        return HttpResponse('You do not have permission to view this page')

    # Get account related metrics
    total_active_accounts = Client.objects.filter(status=1)
    total_active_seo = Client.objects.filter(status=1).filter(has_seo=True).count()
    total_active_cro = Client.objects.filter(status=1).filter(has_cro=True).count()

    # Members
    members = Member.objects.all()

    # Total management fee
    total_management_fee = 0.0
    total_allocated_hours = 0.0

    for aa in total_active_accounts:
        total_management_fee += aa.totalFee
        total_allocated_hours += aa.allHours

    # hours worked this month
    now   = datetime.datetime.now()
    month = now.month
    year  = now.year
    total_hours_worked = AccountHourRecord.objects.filter(month=month, year=year).aggregate(Sum('hours'))['hours__sum']

    context = {
        'total_active_accounts' : total_active_accounts.count(),
        'total_active_seo' : total_active_seo,
        'total_active_cro' : total_active_cro,
        'total_fee' : total_management_fee,
        'total_allocated_hours' : total_allocated_hours,
        'total_hours_worked' : total_hours_worked
    }

    return render(request, 'reports/agency_overview.html', context)
