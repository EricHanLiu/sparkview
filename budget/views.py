# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from adwords_dashboard.models import DependentAccount, Campaign
from bing_dashboard.models import BingAccounts, BingAnomalies, BingCampaign
from budget.models import Client, ClientHist, FlightBudget, CampaignGrouping
import calendar
import json
from datetime import datetime
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
# from dashboard.decorators import cache_on_auth


# Create your views here.
@login_required
@xframe_options_exempt
def index():
    return redirect(index_budget)


@login_required
@xframe_options_exempt
def index_budget(request):

    now = datetime.now()
    days = calendar.monthrange(now.year, now.month)[1]

    if request.method == 'GET':
        items = []
        try:
            accounts = DependentAccount.objects.filter(blacklisted='False')
            for acc in accounts:
                item = {'account': acc}
                items.append(item)
            return render(request, 'budget/adwords_budget.html', {'items': items})
        except ValueError:
            raise Http404

    elif request.method == 'POST':
        try:
            account = DependentAccount.objects.get(dependent_account_id=request.POST['acc_id'])
            desired_spend = request.POST['desired_spend']
            account.desired_spend = desired_spend
            account.dependent_OVU = (float(account.current_spend) / (float(account.desired_spend) / days * now.day)) * 100
            account.save()
            context = {
                'error': 'OK',
                'OVU': account.dependent_OVU
            }
            return JsonResponse(context)
        except ValueError:
            raise Http404


@login_required
@xframe_options_exempt
def bing_budget(request):

    if request.method == 'GET':
        items = []
        try:
            accounts = BingAccounts.objects.filter(blacklisted='False')
            for acc in accounts:
                item = {'account': acc}
                items.append(item)
            return render(request, 'budget/bing_budget.html', {'items': items})
        except ValueError:
            raise Http404

    elif request.method == 'POST':
        try:
            account = BingAccounts.objects.get(account_id=request.POST['acc_id'])
            desired_spend = request.POST['desired_spend']
            account.desired_spend = desired_spend
            account.account_ovu = int(float(account.current_spend) / float(account.desired_spend) * float(100))
            account.save()
            context = {
                'error': 'OK',
                'OVU': account.account_ovu
            }
            return JsonResponse(context)
        except ValueError:
            raise Http404


@login_required
@xframe_options_exempt
def add_client(request):

    aw = []
    bng = []

    now = datetime.now()
    current_day = now.day
    days = calendar.monthrange(now.year, now.month)[1]
    remaining = days - current_day

    black_marker = (current_day * 100) / days

    if request.method == 'GET':
        try:
            context = {}
            clients = Client.objects.all()
            adwords_accounts = DependentAccount.objects.filter(blacklisted=False)
            bing_accounts = BingAccounts.objects.filter(blacklisted=False)
            # facebook_accounts = FacebookAccount.objects.filter(blacklisted=False)
            context['clients'] = clients
            context['adwords'] = adwords_accounts
            context['bing'] = bing_accounts
            context['remaining'] = remaining
            context['no_of_days'] = days
            context['blackmarker'] = round(black_marker, 2)
            return render(request, 'budget/clients.html', context)
        except ValueError:
            raise Http404

    elif request.method == 'POST':

        name = request.POST.get('client_name')
        budget = 0
        adwords_accounts = request.POST.getlist('adwords')
        bing_accounts = request.POST.getlist('bing')

        if adwords_accounts:
            for a in adwords_accounts:
                # noofaccounts = len(adwords_accounts)
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                spend = request.POST.get('aw_budget_'+a)
                # if bing_accounts:
                #     aw_acc.desired_spend = int(budget)/2/noofaccounts
                # else:
                #     aw_acc.desired_spend = int(budget)/noofaccounts
                aw_acc.desired_spend = int(spend)
                budget += int(spend)
                aw_acc.save()
                aw.append(aw_acc)

        if bing_accounts:
            for b in bing_accounts:
                spend = request.POST.get('bing_budget_'+b)
                # noofaccounts = len(bing_accounts)
                bing_acc = BingAccounts.objects.get(account_id=b)
                # if adwords_accounts:
                #     bing_acc.desired_spend = int(budget)/2/noofaccounts
                # else:
                #     bing_acc.desired_spend = int(budget)/noofaccounts
                bing_acc.desired_spend = int(spend)
                budget += int(spend)
                bing_acc.save()
                bng.append(bing_acc)

        new_client = Client.objects.create(client_name=name, budget=budget)

        if aw:
            for acc in aw:
                new_client.adwords.add(acc)
                new_client.current_spend += acc.current_spend
                new_client.aw_spend += acc.current_spend
                new_client.aw_budget += acc.desired_spend
                new_client.save()

        if bng:
            for bacc in bng:
                new_client.bing.add(bacc)
                new_client.current_spend += bacc.current_spend
                new_client.bing_spend += bacc.current_spend
                new_client.bing_budget += bacc.desired_spend
                new_client.save()

        context = {}
        # facebook_accounts = request.POST.getlist('facebook')
        return JsonResponse(context)

# def get_flight_dates():
#     pass


@login_required
@xframe_options_exempt
def client_details(request, client_id):

    now = datetime.now()
    current_day = now.day
    days = calendar.monthrange(now.year, now.month)[1]
    remaining = days - current_day + 1
    black_marker = (current_day * 100) / days

    if request.method == 'GET':
        try:
            client = Client.objects.get(id=client_id)
            # flight_budgets = FlightBudget.objects.get()
            context = {
                'client_data': client,
                'today': current_day,
                'no_of_days': days,
                'remaining': remaining,
                'blackmarker': round(black_marker, 2)
            }
            return render(request, 'budget/view_client.html', context)
        except ValueError:
            raise Http404


@login_required
@xframe_options_exempt
def delete_clients(request):

    context = {}

    if request.method == 'GET':
        return HttpResponse('What are you looking for here?')

    elif request.method == 'POST':

        client_ids = request.POST.getlist('client_ids[]')

        if client_ids:
            for client in client_ids:
                rip_client = Client.objects.get(id=client)
                rip_client.delete()
                context['status'] = 'success'
        else:
            context['status'] = 'no data received'

        return JsonResponse(context)


@login_required
@xframe_options_exempt
def last_month(request):

    if request.method == 'GET':
        try:
            context = {}
            hist_clients = ClientHist.objects.all()
            adwords_accounts = DependentAccount.objects.filter(blacklisted=False)
            bing_accounts = BingAccounts.objects.filter(blacklisted=False)
            # facebook_accounts = FacebookAccount.objects.filter(blacklisted=False)
            context['clients'] = hist_clients
            context['adwords'] = adwords_accounts
            context['bing'] = bing_accounts
            return render(request, 'budget/last_month.html', context)
        except ValueError:
            raise Http404


@login_required
@xframe_options_exempt
def hist_client_details(request, client_id):

    now = datetime.now()
    current_day = now.day
    days = calendar.monthrange(now.year, now.month)[1]
    remaining = days - current_day


    if request.method == 'GET':
        try:
            client = ClientHist.objects.get(id=client_id)
            context = {
                'client_data': client,
                'today': current_day,
                'no_of_days': days,
                'remaining': remaining
            }
            return render(request, 'budget/view_client_hist.html', context)
        except ValueError:
            raise Http404

def gen_6_months():

    months = []

    for i in range(6):
        i += 1
        next_month = date.today() + relativedelta(months=+i)
        month_name = calendar.month_name[next_month.month]
        months.append(month_name)

    return months


@login_required
@xframe_options_exempt
def sixm_budget(request, client_id):

    if request.method == 'GET':
        try:
            client = Client.objects.get(id=client_id)
            context = {
                'client_data': client,
                'months': gen_6_months()
            }
            return render(request, 'budget/six_months.html', context)
        except ValueError:
            raise Http404

    elif request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        acc_id = data['acc_id']
        budgets = data['budgets']

        try:
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
        except:
            account = BingAccounts.objects.get(account_id=acc_id)

        account.ds1 = budgets[0]
        account.ds2 = budgets[1]
        account.ds3 = budgets[2]
        account.ds4 = budgets[3]
        account.ds5 = budgets[4]
        account.ds6 = budgets[5]
        account.save()

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)


@login_required
@xframe_options_exempt
def flight_dates(request):

    if request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        acc_id = data['acc_id']
        start_date = data['sdate']
        end_date = data['edate']
        budget = data['budget']

        try:
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            FlightBudget.objects.create(budget=budget, start_date=start_date, end_date=end_date,
                                        adwords_account=account)
        except:
            account = BingAccounts.objects.get(account_id=acc_id)
            FlightBudget.objects.create(budget=budget, start_date=start_date, end_date=end_date,
                                        bing_account=account)

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)


@login_required
@xframe_options_exempt
def detailed_flight_dates(request, account_id):

    try:
        account = DependentAccount.objects.get(dependent_account_id=account_id)
        budgets = FlightBudget.objects.filter(adwords_account=account)
        platform_type = 'AW'
    except:
        account = BingAccounts.objects.get(account_id=account_id)
        budgets = FlightBudget.objects.filter(bing_account=account)
        platform_type = 'BING'

    context = {
        'platform_type': platform_type,
        'account': account,
        'budgets': budgets
    }

    return render(request, 'budget/flight_dates.html', context)


@login_required
@xframe_options_exempt
def campaign_groupings(request, account_id):

    cmps = []

    if request.method == 'GET':
        try:
            account = DependentAccount.objects.get(dependent_account_id=account_id)
            campaigns = Campaign.objects.filter(account=account, groupped=False)
            groups = CampaignGrouping.objects.filter(adwords=account)
            platform_type = 'AW'
        except:
            account = BingAccounts.objects.get(account_id=account_id)
            campaigns = BingCampaign.objects.filter(account=account)
            groups = CampaignGrouping.objects.filter(bing=account)
            platform_type = 'BING'

        context = {
            'platform_type': platform_type,
            'account': account,
            'campaigns': campaigns,
            'groups': groups
        }

        return render(request, 'budget/campaign_groupings.html', context)

    elif request.method == 'POST':

        campaigns = request.POST.getlist('campaigns')

        try:
            account = DependentAccount.objects.get(dependent_account_id=account_id)
            new_grouping = CampaignGrouping.objects.create(adwords=account)

            if campaigns:
                for cmp in campaigns:
                    cmp_obj = Campaign.objects.get(campaign_id=cmp)
                    budget = request.POST.get('grouping-budget')
                    cmp_obj.campaign_budget = int(budget)/len(campaigns)
                    cmp_obj.groupped = True
                    cmp_obj.save()
                    cmps.append(cmp_obj)

            if cmps:
                for c in cmps:
                    new_grouping.aw_campaigns.add(c)
                    new_grouping.current_spend += c.campaign_cost
                    new_grouping.budget += c.campaign_budget
                    new_grouping.save()

        except:
            account = BingAccounts.objects.get(account_id=account_id)
            new_grouping = CampaignGrouping.objects.create(bing=account)

            if campaigns:
                for cmp in campaigns:
                    cmp_obj = BingCampaign.objects.get(campaign_id=cmp)
                    budget = request.POST.get('grouping-budget')
                    cmp_obj.campaign_budget = int(budget)/len(campaigns)
                    cmp_obj.groupped = True
                    cmp_obj.save()
                    cmps.append(cmp_obj)

            if cmps:
                for c in cmps:
                    new_grouping.bing_campaigns.add(c)
                    new_grouping.current_spend += c.campaign_cost
                    new_grouping.budget += c.campaign_budget
                    new_grouping.save()

        context = {}

        return JsonResponse(context)


@login_required
def update_groupings(request):

    if request.method == 'POST':

        data = request.POST

        gr_id = data['id']
        budget = data['budget']
        grouping = CampaignGrouping.objects.get(id=gr_id)
        grouping.budget = int(budget)
        grouping.save()

        for c in grouping.aw_campaigns.all():
            c.campaign_budget = int(budget)/len(grouping.aw_campaigns.all())
            c.save()

        context = {}
        return JsonResponse(context)


@login_required
def delete_groupings(request):

    if request.method == 'POST':

        data = request.POST.getlist('grouping_ids')

        for gr_id in data:
            grouping = CampaignGrouping.objects.get(id=gr_id)
            if len(grouping.aw_campaigns.all()) > 0:
                for cmp in grouping.aw_campaigns.all():
                    cmp.groupped = False
                    cmp.save()
            else:
                for cmp in grouping.bing_campaigns.all():
                    cmp.groupped = False
                    cmp.save()

            grouping.delete()

        context = {}

        return JsonResponse(context)