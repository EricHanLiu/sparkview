# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from adwords_dashboard.models import DependentAccount, Campaign
from bing_dashboard.models import BingAccounts, BingCampaign
from facebook_dashboard.models import FacebookAccount, FacebookCampaign
from budget.models import Client, ClientHist, FlightBudget, CampaignGrouping
import calendar
import json
from datetime import datetime
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

    if request.method == 'GET':
        accounts = DependentAccount.objects.filter(blacklisted='False')
        return render(request, 'budget/adwords_budget.html', {'items': accounts})

    elif request.method == 'POST':
        account = DependentAccount.objects.get(dependent_account_id=request.POST['acc_id'])
        desired_spend = request.POST['desired_spend']
        account.desired_spend = desired_spend
        account.save()
        context = {
            'error': 'OK',
        }

        return JsonResponse(context)


@login_required
@xframe_options_exempt
def bing_budget(request):

    if request.method == 'GET':
        try:
            accounts = BingAccounts.objects.filter(blacklisted='False')
            return render(request, 'budget/bing_budget.html', {'items': accounts})
        except ValueError:
            raise Http404

    elif request.method == 'POST':
        try:
            account = BingAccounts.objects.get(account_id=request.POST['acc_id'])
            desired_spend = request.POST['desired_spend']
            account.desired_spend = desired_spend
            account.save()
            context = {
                'error': 'OK',
            }
            return JsonResponse(context)
        except ValueError:
            raise Http404

@login_required
@xframe_options_exempt
def facebook_budget(request):

    if request.method == 'GET':
        try:
            accounts = FacebookAccount.objects.filter(blacklisted='False')
            return render(request, 'budget/facebook_budget.html', {'items': accounts})
        except ValueError:
            raise Http404

    elif request.method == 'POST':
        try:
            account = FacebookAccount.objects.get(account_id=request.POST['acc_id'])
            desired_spend = request.POST['desired_spend']
            account.desired_spend = desired_spend
            account.save()
            context = {
                'error': 'OK',
            }
            return JsonResponse(context)
        except ValueError:
            raise Http404


@login_required
@xframe_options_exempt
def add_client(request):

    aw = []
    bng = []
    fb = []

    today = datetime.today()
    next_month = datetime(
        year=today.year,
        month=((today.month + 1) % 12),
        day=1
    )
    lastday_month = next_month + relativedelta(days=-1)
    black_marker = (today.day / lastday_month.day) * 100
    remaining = lastday_month.day - today.day

    if request.method == 'GET':
        context = {}
        clients = Client.objects.all()
        adwords_accounts = DependentAccount.objects.filter(blacklisted=False)
        bing_accounts = BingAccounts.objects.filter(blacklisted=False)
        facebook_accounts = FacebookAccount.objects.filter(blacklisted=False)
        context['clients'] = clients
        context['adwords'] = adwords_accounts
        context['bing'] = bing_accounts
        context['facebook'] = facebook_accounts
        context['remaining'] = remaining
        context['no_of_days'] = lastday_month.day
        context['blackmarker'] = round(black_marker, 2)

        return render(request, 'budget/clients.html', context)

    elif request.method == 'POST':

        name = request.POST.get('client_name')
        budget = 0
        # suggested budget / global budget
        has_gts = request.POST.get('global_target_spend')
        gts_value = request.POST.get('gts_value')
        adwords_accounts = request.POST.getlist('adwords')
        bing_accounts = request.POST.getlist('bing')
        facebook_accounts = request.POST.getlist('facebook')

        new_client = Client.objects.create(client_name=name)

        if has_gts == '1':
            new_client.has_gts = True
            new_client.target_spend = gts_value

        elif has_gts == '0':
            new_client.has_budget = True

        if adwords_accounts:
            for a in adwords_accounts:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                spend = request.POST.get('aw_budget_'+a)

                if spend:
                    aw_acc.desired_spend = float(spend)
                    budget += int(spend)
                    aw_acc.save()
                aw.append(aw_acc)

        if bing_accounts:
            for b in bing_accounts:
                spend = request.POST.get('bing_budget_' + b)
                bing_acc = BingAccounts.objects.get(account_id=b)

                if spend:
                    bing_acc.desired_spend = float(spend)
                    budget += int(spend)
                    bing_acc.save()
                bng.append(bing_acc)

        if facebook_accounts:
            for f in facebook_accounts:
                spend = request.POST.get('facebook_budget_' + f)
                fb_acc = FacebookAccount.objects.get(account_id=f)

                if spend:
                    fb_acc.desired_spend = float(spend)
                    budget += float(spend)
                    fb_acc.save()
                fb.append(fb_acc)

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

        if fb:
            for facc in fb:
                new_client.facebook.add(facc)
                new_client.current_spend += facc.current_spend
                new_client.fb_spend += facc.current_spend
                new_client.fb_budget += facc.desired_spend
                new_client.save()

        context = {}

        return JsonResponse(context)


@login_required
@xframe_options_exempt
def client_details(request, client_id):

    today = datetime.today() - relativedelta(days=1)
    next_month = datetime(
        year=today.year,
        month=((today.month + 1) % 12),
        day=1
    )
    lastday_month = next_month + relativedelta(days=-1)
    black_marker = (today.day / lastday_month.day) * 100
    remaining = lastday_month.day - today.day

    if request.method == 'GET':
        client = Client.objects.get(id=client_id)
        context = {
            'client_data': client,
            'today': today.day,
            'no_of_days': lastday_month.day,
            'remaining': remaining,
            'blackmarker': round(black_marker, 2)
        }

        return render(request, 'budget/view_client.html', context)

    elif request.method == 'POST':
        # param: account_id
        aid = request.POST.get('aid')
        # param: client_id
        cid = request.POST.get('cid')
        budget = request.POST.get('budget')
        target_spend = request.POST.get('target_spend')
        channel = request.POST.get('channel')


        if channel == 'adwords':
            account = DependentAccount.objects.get(dependent_account_id=aid)
            account.desired_spend = budget
            account.save()
            context = {
                'aid': account.dependent_account_id,
                'aname': account.dependent_account_name,
                'budget': account.desired_spend
            }

        elif channel == 'bing':
            account = BingAccounts.objects.get(account_id=aid)
            account.desired_spend = budget
            account.save()
            context = {
                'aid': account.account_id,
                'aname': account.account_name,
                'budget': account.desired_spend
            }

        elif channel == 'facebook':
            account = FacebookAccount.objects.get(account_id=aid)
            account.desired_spend = budget
            account.save()
            context = {
                'aid': account.account_id,
                'aname': account.account_name,
                'budget': account.desired_spend
            }

        else:

            client = Client.objects.get(id=cid)
            client.target_spend = target_spend
            client.save()

            context = {
                'client': client.client_name,
                'target_spend': client.target_spend,
                'error_message': 'Please enter a value greater than 0(zero).',
            }

        return JsonResponse(context)


@login_required
@xframe_options_exempt
def delete_clients(request):

    deleted_clients = []

    if request.method == 'POST':

        client_ids = request.POST.getlist('client_ids')

        if client_ids:
            for client in client_ids:
                rip_client = Client.objects.get(id=client)
                client = {
                    'name': rip_client.client_name,
                    'id': rip_client.id
                }
                deleted_clients.append(client)
                rip_client.delete()
            context = {
                'deleted': deleted_clients
            }
        else:
            context = {
                'status': 'No data received'
            }

        return JsonResponse(context)


@login_required
@xframe_options_exempt
def last_month(request):

    if request.method == 'GET':
        context = {}
        context['facebook'] = FacebookAccount.objects.filter(blacklisted=False)
        context['clients'] = ClientHist.objects.all()
        context['adwords'] = DependentAccount.objects.filter(blacklisted=False)
        context['bing'] = BingAccounts.objects.filter(blacklisted=False)
        context['facebook'] = FacebookAccount.objects.filter(blacklisted=False)

        return render(request, 'budget/last_month.html', context)


@login_required
@xframe_options_exempt
def hist_client_details(request, client_id):

    today = datetime.today() - relativedelta(days=1)
    next_month = datetime(
        year=today.year,
        month=((today.month + 1) % 12),
        day=1
    )
    lastday_month = next_month + relativedelta(days=-1)
    black_marker = (today.day / lastday_month.day) * 100
    remaining = lastday_month.day - today.day

    if request.method == 'GET':
        client = ClientHist.objects.get(id=client_id)
        context = {
            'client_data': client,
            'today': today.day,
            'no_of_days': lastday_month.day,
            'remaining': remaining
        }

        return render(request, 'budget/view_client_hist.html', context)

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
        client = Client.objects.get(id=client_id)

        context = {
            'client_data': client,
            'months': gen_6_months()
        }

        return render(request, 'budget/six_months.html', context)

    elif request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        acc_id = data['acc_id']
        budgets = data['budgets']
        channel = data['channel']

        if channel == 'adwords':
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
        elif channel == 'bing':
            account = BingAccounts.objects.get(account_id=acc_id)
        elif channel == 'facebook':
            account = FacebookAccount.objects.get(account_id=acc_id)

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
def flight_dates(request):

    if request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        acc_id = data['acc_id']
        start_date = data['sdate']
        end_date = data['edate']
        budget = data['budget']
        channel = data['channel']

        if channel == 'adwords':
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            FlightBudget.objects.create(budget=budget, start_date=start_date, end_date=end_date,
                                        adwords_account=account)
        elif channel == 'bing':
            account = BingAccounts.objects.get(account_id=acc_id)
            FlightBudget.objects.create(budget=budget, start_date=start_date, end_date=end_date,
                                        bing_account=account)

        elif channel == 'facebook':
            account = FacebookAccount.objects.get(account_id=acc_id)
            FlightBudget.objects.create(budget=budget, start_date=start_date, end_date=end_date,
                                        facebook_account=account)

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)


@login_required
def detailed_flight_dates(request):

    account_id = request.GET.get('account_id')
    channel = request.GET.get('channel')
    context = {}

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
        context['account'] = account
        context['budgets'] = FlightBudget.objects.filter(adwords_account=account)
        context['platform_type'] = 'AW'
        return render(request, 'budget/flight_dates.html', context)

    if channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
        context['account'] = account
        context['budgets'] = FlightBudget.objects.filter(bing_account=account)
        context['platform_type'] = 'BING'
        return render(request, 'budget/flight_dates.html', context)

    if channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)
        context['account'] = account
        context['budgets'] = FlightBudget.objects.filter(facebook_account=account)
        context['platform_type'] = 'FACEBOOK'
        return render(request, 'budget/flight_dates.html', context)


@login_required
def campaign_groupings(request):

    account_id = request.GET.get('account_id')
    channel =  request.GET.get('channel')

    if request.method == 'GET':

        if channel == 'adwords':
            account = DependentAccount.objects.get(dependent_account_id=account_id)
            campaigns = Campaign.objects.filter(account=account, groupped=False)
            groups = CampaignGrouping.objects.filter(adwords=account)
            platform_type = 'AW'

        elif channel == 'bing':
            account = BingAccounts.objects.get(account_id=account_id)
            campaigns = BingCampaign.objects.filter(account=account, groupped=False)
            groups = CampaignGrouping.objects.filter(bing=account)
            platform_type = 'BING'

        elif channel == 'facebook':
            account = FacebookAccount.objects.get(account_id=account_id)
            campaigns = FacebookCampaign.objects.filter(account=account, groupped=False)
            groups = CampaignGrouping.objects.filter(facebook=account)
            platform_type = 'FB'

        context = {
            'platform_type': platform_type,
            'account': account,
            'campaigns': campaigns,
            'groups': groups
        }

        return render(request, 'budget/campaign_groupings.html', context)

    elif request.method == 'POST':

        cmps = []
        campaigns = request.POST.getlist('campaigns')
        campaigns = set(campaigns)
        channel = request.POST.get('channel')

        if channel == 'adwords':
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

        elif channel == 'bing':
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

        elif channel == 'facebook':
            account = FacebookAccount.objects.get(account_id=account_id)
            new_grouping = CampaignGrouping.objects.create(facebook=account)

            if campaigns:
                for cmp in campaigns:
                    cmp_obj = FacebookCampaign.objects.get(campaign_id=cmp)
                    budget = request.POST.get('grouping-budget')
                    cmp_obj.campaign_budget = int(budget)/len(campaigns)
                    cmp_obj.groupped = True
                    cmp_obj.save()
                    cmps.append(cmp_obj)

            if cmps:
                for c in cmps:
                    new_grouping.fb_campaigns.add(c)
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

        if len(grouping.aw_campaigns.all()) > 0:

            for cmp in grouping.aw_campaigns.all():
                cmp.campaign_budget = int(budget)/len(grouping.aw_campaigns.all())
                cmp.save()

        elif len(grouping.bing_campaigns.all()) > 0:

            for cmp in grouping.bing_campaigns.all():
                cmp.campaign_budget = int(budget)/len(grouping.bing_campaigns.all())
                cmp.save()

        elif len(grouping.fb_campaigns.all()) > 0:

            for cmp in grouping.fb_campaigns.all():
                cmp.campaign_budget = int(budget)/len(grouping.fb_campaigns.all())
                cmp.save()

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
            elif len(grouping.bing_campaigns.all()) > 0:
                for cmp in grouping.bing_campaigns.all():
                    cmp.groupped = False
                    cmp.save()
            elif len(grouping.fb_campaigns.all()) > 0:
                for cmp in grouping.fb_campaigns.all():
                    cmp.groupped = False
                    cmp.save()

            grouping.delete()

        context = {}

        return JsonResponse(context)

# Update client budgets
@login_required
def update_budget(request):

    if request.method == 'POST':

        data = request.POST
        client_id = data['id']
        client = Client.objects.get(id=client_id)

        if 'budget' in data and int(data['budget']) > 0:
            budget = data['budget']
            client.budget = budget
            width = (client.current_spend / int(budget)) * 100
            gts_budget = 'budget'

        if 'target_spend' in data and int(data['target_spend']) > 0:
            target_spend = data['target_spend']
            client.target_spend = target_spend
            width = (client.current_spend / int(target_spend)) * 100
            gts_budget = 'gts'

        client.save()

        if 90 < width < 100:
            pb_color = 'bg-success'

        elif 0 < width <= 90:
            pb_color = 'bg-warning'

        else:
            pb_color = 'bg-danger'

        context = {
            'width':  round(width, 2),
            'client_id': client_id,
            'client_name': client.client_name,
            'pb_color': pb_color,
            'gts_budget': gts_budget
        }

        return JsonResponse(context)


# Update flight budgets
@login_required
def update_fbudget(request):

    context = {}

    if request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        budget_id = data['budget_id']
        budget = data['budget']
        sdate = data['sdate']
        edate = data['edate']
        fbudget = FlightBudget.objects.get(id=budget_id)
        fbudget.budget = budget
        fbudget.start_date = sdate
        fbudget.end_date = edate
        fbudget.save()

        return JsonResponse(context)


# Delete flight budgets
@login_required
def delete_fbudget(request):

    if request.method == 'POST':

        data = request.POST.getlist('flight_budgets')
        for fb_id in data:
            fbudget = FlightBudget.objects.get(id=fb_id)
            fbudget.delete()

        context = {}

        return JsonResponse(context)

@login_required
def gts_or_budget(request):

    data = request.POST
    client = Client.objects.get(id=data['cid'])

    context = {
        'client_name': client.client_name,
    }

    if 'gts' in data and data['gts'] == 'on':
        client.has_gts = True
        client.save()
        context['gtson'] = '1'

    elif 'gts' in data and data['gts'] == 'off':
        client.has_gts = False
        client.save()
        context['gtsoff'] = '1'

    elif 'budget' in data and data['budget'] == 'on':
        client.has_budget = True
        client.save()
        context['budgeton'] = '1'

    elif 'budget' in data and data['budget'] == 'off':
        client.has_budget = False
        client.save()
        context['budgetoff'] = '1'

    return JsonResponse(context)