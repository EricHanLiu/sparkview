# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseForbidden
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Q, ObjectDoesNotExist
from adwords_dashboard.models import DependentAccount, Campaign
from bing_dashboard.models import BingAccounts, BingCampaign
from facebook_dashboard.models import FacebookAccount, FacebookCampaign
from budget.models import Client, ClientHist, CampaignGrouping, ClientCData, BudgetUpdate, Budget, CampaignExclusions
from user_management.models import Member
from django.core import serializers
from tasks import adwords_tasks
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar


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

    today = datetime.today() - relativedelta(days=1)
    next_month_int = today.month + 1
    if next_month_int == 13:
        next_month_int = 1
    next_month = datetime(
        year=today.year,
        month=next_month_int,
        day=1
    )
    lastday_month = next_month + relativedelta(days=-1)
    black_marker = (today.day / lastday_month.day) * 100
    remaining = lastday_month.day - today.day

    if request.method == 'GET':
        context = {}
        clients = Client.objects.all().order_by('client_name')
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
        context['status_badges'] = ['info', 'success', 'warning', 'danger']

        return render(request, 'budget/clients.html', context)

    elif request.method == 'POST':

        new_aw = []
        new_bing = []
        new_fb = []
        data = request.POST

        name = request.POST.get('client_name')
        budget = 0
        # suggested budget / global budget
        has_gts = request.POST.get('global_target_spend')
        gts_value = request.POST.get('gts_value')
        adwords_accounts = request.POST.getlist('adwords')
        bing_accounts = request.POST.getlist('bing')
        facebook_accounts = request.POST.getlist('facebook')

        for i in range(len(adwords_accounts)):
            tmp_val = adwords_accounts[i].split('|')
            new_aw.append(tmp_val[0])

        for i in range(len(bing_accounts)):
            tmp_val = bing_accounts[i].split('|')
            new_bing.append(tmp_val[0])

        for i in range(len(facebook_accounts)):
            tmp_val = facebook_accounts[i].split('|')
            new_fb.append(tmp_val[0])

        new_client = Client.objects.create(client_name=name)

        if has_gts == '1':
            new_client.has_gts = True
            new_client.target_spend = gts_value

        elif has_gts == '0' or not has_gts:
            new_client.has_budget = True

        if adwords_accounts:
            for a in new_aw:

                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                spend = request.POST.get('aw_budget_' + a)

                # Checks if we have a budget to set
                # If not set it to 0
                if spend:
                    continue
                else:
                    spend = 0.0

                networks = request.POST.getlist('networks')

                if 'All' in networks and len(networks) == 1:
                    aw_acc.desired_spend = float(spend)
                    budget += float(spend)

                aw_acc.save()
                aw.append(aw_acc)

        if bing_accounts:
            for b in new_bing:
                bing_acc = BingAccounts.objects.get(account_id=b)
                spend = request.POST.get('bing_budget_' + b)

                if spend:
                    bing_acc.desired_spend = float(spend)
                    budget += float(spend)
                    bing_acc.save()
                bng.append(bing_acc)

        if facebook_accounts:
            for f in new_fb:
                fb_acc = FacebookAccount.objects.get(account_id=f)
                spend = request.POST.get('facebook_budget_' + f)

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

        adwords_tasks.cron_clients.delay()

        return JsonResponse(context)


@login_required
@xframe_options_exempt
def client_details(request, client_id):
    today = datetime.today() - relativedelta(days=1)  # This is actually yesterday
    next_month_int = today.month + 1
    if next_month_int == 13:
        next_month_int = 1
    next_month = datetime(
        year=today.year,
        month=next_month_int,
        day=1
    )
    lastday_month = next_month + relativedelta(days=-1)
    black_marker = (today.day / lastday_month.day) * 100
    remaining = lastday_month.day - today.day

    if request.method == 'GET':
        client = Client.objects.get(id=client_id)
        cmp_groupings = CampaignGrouping.objects.filter(client=client)
        chdata = ClientCData.objects.filter(client=client)
        chdata_json = json.loads(serializers.serialize("json", chdata))

        budget_updated_for_month, created = BudgetUpdate.objects.get_or_create(account=client, month=today.month,
                                                                               year=today.year)

        status_badges = ['info', 'success', 'warning', 'danger']

        context = {
            'client_data': client,
            'today': today.day,
            'no_of_days': lastday_month.day,
            'current_month': calendar.month_name[today.month],
            'remaining': remaining,
            'blackmarker': round(black_marker, 2),
            'adwords': DependentAccount.objects.filter(blacklisted=False),
            'bing': BingAccounts.objects.filter(blacklisted=False),
            'facebook': FacebookAccount.objects.filter(blacklisted=False),
            'chdata': chdata_json[0]['fields'] if chdata_json else {},
            'status_badges': status_badges,
            'groupings': cmp_groupings,
            'budget_updated_for_month': budget_updated_for_month
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
            account.desired_spend = int(float(budget))
            account.save()
            context = {
                'aid': account.dependent_account_id,
                'aname': account.dependent_account_name,
                'budget': account.desired_spend
            }

        elif channel == 'bing':
            account = BingAccounts.objects.get(account_id=aid)
            account.desired_spend = int(float(budget))
            account.save()
            context = {
                'aid': account.account_id,
                'aname': account.account_name,
                'budget': account.desired_spend
            }

        elif channel == 'facebook':
            account = FacebookAccount.objects.get(account_id=aid)
            account.desired_spend = int(float(budget))
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
        context = {
            'clients': ClientHist.objects.all(),
            'adwords': DependentAccount.objects.filter(blacklisted=False),
            'bing': BingAccounts.objects.filter(blacklisted=False),
            'facebook': FacebookAccount.objects.filter(blacklisted=False)
        }

        return render(request, 'budget/last_month.html', context)


@login_required
@xframe_options_exempt
def hist_client_details(request, client_id):
    today = datetime.today() - relativedelta(days=1)
    next_month_int = today.month + 1
    if next_month_int == 13:
        next_month_int = 1
    next_month = datetime(
        year=today.year,
        month=next_month_int,
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
        """
        Temporary overriding this with a new approach to flight dates in an attempt to simplify the concept for the members
        May come back to this later
        """
        data = json.loads(request.body.decode('utf-8'))
        acc_id = data['acc_id']
        start_date = data['sdate']
        end_date = data['edate']
        budget = data['budget']
        channel = data['channel']

        if channel == 'adwords':
            account = DependentAccount.objects.get(dependent_account_id=acc_id)

        elif channel == 'bing':
            account = BingAccounts.objects.get(account_id=acc_id)

        elif channel == 'facebook':
            account = FacebookAccount.objects.get(account_id=acc_id)

        account.desired_spend_start_date = datetime.strptime(start_date, '%Y-%m-%d')
        account.desired_spend_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        account.save()

        print(account.desired_spend_end_date)

        context = {
            'resp': 'OK'
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
        context['platform_type'] = 'AW'
        return render(request, 'budget/flight_dates.html', context)

    if channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
        context['account'] = account
        context['platform_type'] = 'BING'
        return render(request, 'budget/flight_dates.html', context)

    if channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)
        context['account'] = account
        context['platform_type'] = 'FACEBOOK'
        return render(request, 'budget/flight_dates.html', context)


@login_required
def campaign_groupings(request):
    account_id = request.GET.get('account_id')
    channel = request.GET.get('channel')

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
                    cmp = cmp.split("|")
                    cmp_obj = Campaign.objects.get(campaign_id=cmp[0])
                    budget = request.POST.get('grouping-budget')
                    cmp_obj.campaign_budget = int(budget) / len(campaigns)
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
                    cmp = cmp.split("|")
                    cmp_obj = BingCampaign.objects.get(campaign_id=cmp[0])
                    budget = request.POST.get('grouping-budget')
                    cmp_obj.campaign_budget = int(budget) / len(campaigns)
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
                    cmp = cmp.split("|")
                    cmp_obj = FacebookCampaign.objects.get(campaign_id=cmp[0])
                    budget = request.POST.get('grouping-budget')
                    cmp_obj.campaign_budget = int(budget) / len(campaigns)
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
def add_groupings(request):
    if request.method == 'POST':

        # channel = request.POST.get('cgr_channel')
        acc_id = request.POST.get('cgr_acc_id')
        c_id = request.POST.get('cgr_client_id')
        group_name = request.POST.get('cgr_group_name')
        group_by = request.POST.get('cgr_group_by')
        budget = request.POST.get('group_budget')
        campaigns = request.POST.getlist('campaigns')
        flight_date = request.POST.get('cgr_fdate')

        client = Client.objects.get(id=c_id)

        acc_ids = " ".join(acc_id.split()).split(",")
        acc_ids = list(filter(None, acc_ids))

        response = {}

        if group_by == 'text':
            group_by_text = request.POST.get('cgr_group_by_text')
            if group_by_text is None:
                group_by_text = ''
            new_group = CampaignGrouping.objects.create(
                group_name=group_name,
                group_by=group_by_text,
                budget=budget,
                client=client,
                group_type=2
            )
            new_group.update_text_grouping()
        elif group_by == 'all':
            new_group = CampaignGrouping.objects.create(
                group_name=group_name,
                group_by=group_by,
                budget=budget,
                client=client,
                group_type=0
            )
            # Add all the campaigns
            for aa in client.adwords.all():
                campaigns = Campaign.objects.filter(account=aa)
                for cmp in campaigns:
                    new_group.aw_campaigns.add(cmp)
                new_group.save()
            for fa in client.facebook.all():
                campaigns = FacebookCampaign.objects.filter(account=fa)
                for cmp in campaigns:
                    new_group.fb_campaigns.add(cmp)
                new_group.save()
            for ba in client.bing.all():
                campaigns = BingCampaign.objects.filter(account=ba)
                for cmp in campaigns:
                    new_group.bing_campaigns.add(cmp)
                new_group.save()
        elif group_by == 'manual':

            new_group = CampaignGrouping.objects.create(
                group_name=group_name,
                group_by=group_by,
                budget=budget,
                client=client,
                group_type=1
            )

            for c in campaigns:
                try:
                    cmp = Campaign.objects.get(campaign_id=c)
                    new_group.aw_campaigns.add(cmp)
                    new_group.save()
                except Campaign.DoesNotExist:
                    pass

                try:
                    cmp = BingCampaign.objects.get(campaign_id=c)
                    new_group.bing_campaigns.add(cmp)
                    new_group.save()
                except BingCampaign.DoesNotExist:
                    pass

                try:
                    cmp = FacebookCampaign.objects.get(campaign_id=c)
                    new_group.fb_campaigns.add(cmp)
                    new_group.save()
                except FacebookCampaign.DoesNotExist:
                    pass

        if flight_date == 'yes':
            start_date = request.POST.get('cgr_sdate')
            end_date = request.POST.get('cgr_edate')

            new_group.start_date = start_date
            new_group.end_date = end_date
            new_group.save()

        response['group_name'] = new_group.group_name
        # for acc in acc_ids:
        #     try:
        #         adwords = DependentAccount.objects.get(dependent_account_id=acc)
        #         # adwords_tasks.adwords_cron_campaign_stats.delay(adwords.dependent_account_id, client.id)
        #     except ObjectDoesNotExist:
        #         pass
        #     try:
        #         time.sleep(0.5)
        #         bing = BingAccounts.objects.get(account_id=acc)
        #         # bing_tasks.bing_cron_campaign_stats.delay(bing.account_id, client.id)
        #     except ObjectDoesNotExist:
        #         pass
        #     try:
        #         time.sleep(0.5)
        #         facebook = FacebookAccount.objects.get(account_id=acc)
        #         # facebook_tasks.facebook_cron_campaign_stats.delay(facebook.account_id, client.id)
        #     except ObjectDoesNotExist:
        #         pass

        return JsonResponse(response)


@login_required
def update_groupings(request):
    if request.method == 'POST':

        data = request.POST
        gr_id = data['cgr_gr_id']
        budget = data['group_budget']
        group_name = data['cgr_group_name']
        group_by = request.POST.get('cgr_group_by', False)
        group_by_edit = data['cgr_group_by_edit']
        campaigns = request.POST.getlist('campaigns_edit')
        # channel = data['cgr_channel']
        start_date = data['cgr_sdate']
        end_date = data['cgr_edate']

        grouping = CampaignGrouping.objects.get(id=gr_id)
        grouping.budget = float(budget)
        grouping.group_name = group_name

        if start_date and end_date:
            grouping.start_date = start_date
            grouping.end_date = end_date

        if group_by == 'manual':
            for c in campaigns:
                try:
                    if c not in grouping.aw_campaigns.all():

                        cmp = Campaign.objects.get(campaign_id=c)
                        grouping.aw_campaigns.add(cmp)
                        grouping.save()

                        for campaign in grouping.aw_campaigns.all():
                            if campaign.campaign_id not in campaigns:
                                cmp = Campaign.objects.get(campaign_id=c)
                                grouping.aw_campaigns.remove(cmp)
                                grouping.save()

                except ObjectDoesNotExist:
                    pass

                try:
                    if c not in grouping.bing_campaigns.all():
                        cmp = BingCampaign.objects.get(campaign_id=c)
                        grouping.bing_campaigns.add(cmp)
                        grouping.save()

                    for campaign in grouping.bing_campaigns.all():
                        if campaign.campaign_id not in campaigns:
                            cmp = BingCampaign.objects.get(campaign_id=c)
                            grouping.bing_campaigns.remove(cmp)
                            grouping.save()
                except ObjectDoesNotExist:
                    pass

                try:
                    if c not in grouping.fb_campaigns.all():
                        cmp = FacebookCampaign.objects.get(campaign_id=c)
                        grouping.fb_campaigns.add(cmp)
                        grouping.save()

                    for campaign in grouping.fb_campaigns.all():
                        if campaign.campaign_id not in campaigns:
                            cmp = FacebookCampaign.objects.get(campaign_id=c)
                            grouping.fb_campaigns.remove(cmp)
                            grouping.save()
                except ObjectDoesNotExist:
                    pass
        else:
            grouping.group_by = group_by_edit
        grouping.save()
        grouping.update_text_grouping()
        # if grouping.client.adwords:
        #     for a in grouping.client.adwords.all():
        #         adwords_tasks.adwords_cron_campaign_stats.delay(a.dependent_account_id, grouping.client.id)
        # if grouping.client.bing:
        #     time.sleep(0.5)
        #     for b in grouping.client.bing.all():
        #         bing_tasks.bing_cron_campaign_stats.delay(b.account_id, grouping.client.id)
        # if grouping.client.facebook:
        #     time.sleep(0.5)
        #     for f in grouping.client.facebook.all():
        #         facebook_tasks.facebook_cron_campaign_stats.delay(f.account_id, grouping.client.id)

        context = {}

        return JsonResponse(context)


@login_required
def delete_groupings(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        group = CampaignGrouping.objects.get(id=data['gr_id'])
        context = {
            'group_name': group.group_name
        }
        group.delete()

        return JsonResponse(context)


@login_required
def get_accounts(request):
    adwords_accounts = DependentAccount.objects.all()
    fb_accounts = FacebookAccount.objects.all()
    bing_accounts = BingAccounts.objects.all()

    accounts = list(adwords_accounts) + list(fb_accounts) + list(bing_accounts)

    account = get_object_or_404(Client, id=request.POST.get('account_id'))
    existing_aw = account.adwords.all()
    existing_fb = account.facebook.all()
    existing_bing = account.bing.all()

    response = {
        'accounts': json.loads(serializers.serialize('json', accounts)),
        'existing_aw': json.loads(serializers.serialize('json', existing_aw)),
        'existing_fb': json.loads(serializers.serialize('json', existing_fb)),
        'existing_bing': json.loads(serializers.serialize('json', existing_bing))
    }

    return JsonResponse(response)


@login_required
def get_campaigns(request):
    account_id = request.POST.get('account_id')
    account_ids = request.POST.get('account_ids')
    print(account_ids)
    gr_id = request.POST.get('gr_id')
    channel = request.POST.get('channel')

    campaigns = []
    response = {}

    try:
        acc_ids = " ".join(account_ids.split()).split(",")
    except AttributeError:
        acc_ids = []

    # Remove empty strings from list - sanity check
    # We might not have Bing of Facebook accounts assigned to a client
    acc_ids = list(filter(None, acc_ids))

    # Get accounts from DB
    if len(acc_ids) > 0:
        for a in acc_ids:
            try:
                account = DependentAccount.objects.get(dependent_account_id=a)
                # Query for all campaigns regarding the status
                aw_campaigns = Campaign.objects.filter(account=account)
                campaigns.extend(aw_campaigns)
            except (ValueError, ObjectDoesNotExist):
                pass

            try:
                account = BingAccounts.objects.get(account_id=a)
                bing_campaigns = BingCampaign.objects.filter(account=account)
                campaigns.extend(bing_campaigns)
            except ObjectDoesNotExist:
                pass

            try:
                account = FacebookAccount.objects.get(account_id=a)
                fb_campaigns = FacebookCampaign.objects.filter(account=account)
                campaigns.extend(fb_campaigns)
            except (ValueError, ObjectDoesNotExist):
                pass

        response['campaigns'] = json.loads(serializers.serialize('json', campaigns))

    if gr_id:
        gr = CampaignGrouping.objects.filter(id=gr_id)
        gr_json = json.loads(serializers.serialize("json", gr))
        response['group'] = gr_json

    # get excluded campaigns
    account = Client.objects.get(id=account_id)
    try:
        exclusion = CampaignExclusions.objects.get(account=account)
        excluded_campaigns = list(exclusion.aw_campaigns.all()) + list(exclusion.fb_campaigns.all()) + list(
            exclusion.bing_campaigns.all())
    except CampaignExclusions.DoesNotExist:
        excluded_campaigns = []
    response['excluded_campaigns'] = json.loads(serializers.serialize('json', excluded_campaigns))

    return JsonResponse(response)


@login_required
def get_campaigns_in_budget(request):
    budget_id = request.POST.get('budget_id')
    budget = get_object_or_404(Budget, id=budget_id)

    campaigns = list(budget.aw_campaigns_without_excluded) + list(budget.fb_campaigns_without_excluded) + list(
        budget.bing_campaigns_without_excluded)

    response = {
        'campaigns': json.loads(serializers.serialize('json', campaigns))
    }

    return JsonResponse(response)


# Update client budgets
@login_required
def update_budget(request):
    if request.method == 'POST':

        data = request.POST
        client_id = data['id']
        client = Client.objects.get(id=client_id)

        if 'budget' in data and float(data['budget']) > 0:
            budget = data['budget']
            client.budget = budget
            width = (client.current_spend / int(budget)) * 100
            gts_budget = 'budget'

        if 'target_spend' in data and float(data['target_spend']) > 0:
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
            'width': round(width, 2),
            'client_id': client_id,
            'client_name': client.client_name,
            'pb_color': pb_color,
            'gts_budget': gts_budget
        }

        # adwords_tasks.cron_clients.delay()
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


@login_required
def assign_client_accounts(request):
    adwords = request.POST.getlist('adwords')
    bing = request.POST.getlist('bing')
    facebook = request.POST.getlist('facebook')
    client_id = request.POST.get('cid')

    client = Client.objects.get(id=client_id)

    if adwords:
        for a in adwords:
            acc = DependentAccount.objects.get(dependent_account_id=a)
            client.adwords.add(acc)
            client.save()

    if bing:
        for b in bing:
            acc = BingAccounts.objects.get(account_id=b)
            client.bing.add(acc)
            client.save()

    if facebook:
        for f in facebook:
            acc = FacebookAccount.objects.get(account_id=f)
            client.facebook.add(acc)
            client.save()

    response = {
        'client': client.client_name
    }

    adwords_tasks.cron_clients.delay()
    return JsonResponse(response)


@login_required
def disconnect_client_account(request):
    data = request.POST

    channel = data['channel']
    acc_id = data['acc_id']
    client_id = data['client_id']

    response = {}

    if channel == 'adwords':

        account = DependentAccount.objects.get(dependent_account_id=acc_id)
        client = Client.objects.get(id=client_id)

        client.adwords.remove(account)
        client.save()

        response['account'] = account.dependent_account_name

    elif channel == 'bing':

        account = BingAccounts.objects.get(account_id=acc_id)
        client = Client.objects.get(id=client_id)

        client.bing.remove(account)
        client.save()

        response['account'] = account.account_name

    elif channel == 'facebook':

        account = FacebookAccount.objects.get(account_id=acc_id)
        client = Client.objects.get(id=client_id)

        client.facebook.remove(account)
        client.save()

        response['account'] = account.account_name

    return JsonResponse(response)


@login_required
def edit_client_name(request):
    data = request.POST
    client_id = data['cid']
    new_name = data['client_name']

    client = Client.objects.get(id=client_id)
    client.client_name = new_name
    client.save()

    response = {
        'client_name': new_name
    }
    return JsonResponse(response)


@login_required
def edit_flex_budget(request):
    member = Member.objects.get(user=request.user)
    if not request.user.is_staff and not member.has_account(
            int(request.POST.get('account_id'))) and not member.teams_have_accounts(
        int(request.POST.get('account_id'))):
        return HttpResponseForbidden('You do not have permission to view this page')

    account_id = int(request.POST.get('account_id'))
    account = Client.objects.get(id=account_id)

    account.flex_budget = request.POST.get('flex_budget')

    account.save()

    return redirect('/budget/client/' + str(account.id))


@login_required
def confirm_budget(request):
    if request.method != 'POST':
        return HttpResponse('Invalid request type')

    member = Member.objects.get(user=request.user)
    account_id = int(request.POST.get('account_id'))
    if not request.user.is_staff and not member.has_account(account_id) and not member.teams_have_accounts(account_id):
        return HttpResponseForbidden('You do not have permission to view this page')

    now = datetime.now()
    account = Client.objects.get(id=account_id)

    budget_update, created = BudgetUpdate.objects.get_or_create(account=account, month=now.month, year=now.year)
    if budget_update.updated:
        return HttpResponse('Makes no difference')

    budget_update.updated = True
    budget_update.save()

    return HttpResponse('Success')


@login_required
def budget_client_beta(request, account_id):
    """
    New budgets page
    :param request:
    :param account_id:
    :return:
    """
    account = get_object_or_404(Client, id=account_id)
    account_status_classes = ['is-info', 'is-success', 'is-warning', 'is-danger']
    account_status_class = account_status_classes[account.status]

    context = {
        'account': account,
        'account_status_class': account_status_class
    }

    return render(request, 'budget/beta/budgets.html', context)


@login_required
def new_budget(request):
    """
    Creates new budgets
    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request type')

    account = get_object_or_404(Client, id=request.POST.get('account_id'))
    member = request.user.member

    if account not in member.accounts and not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to do this')

    budget = Budget()
    budget.name = request.POST.get('budget_name')
    budget.account = account
    budget.budget = request.POST.get('budget_amount')
    budget.save()

    if 'google_ads' in request.POST:
        budget.has_adwords = True
    if 'facebook_ads' in request.POST:
        budget.has_facebook = True
    if 'bing_ads' in request.POST:
        budget.has_bing = True

    grouping_type = request.POST.get('grouping_type')

    if grouping_type == 'manual':
        # Lousy, but it works for now
        budget.grouping_type = 0
        for c in request.POST.getlist('campaigns'):
            try:
                cmp = Campaign.objects.get(campaign_id=c)
                budget.aw_campaigns.add(cmp)
                budget.save()
            except Campaign.DoesNotExist:
                pass

            try:
                cmp = BingCampaign.objects.get(campaign_id=c)
                budget.bing_campaigns.add(cmp)
                budget.save()
            except BingCampaign.DoesNotExist:
                pass

            try:
                cmp = FacebookCampaign.objects.get(campaign_id=c)
                budget.fb_campaigns.add(cmp)
                budget.save()
            except FacebookCampaign.DoesNotExist:
                pass
    elif grouping_type == 'text':
        budget.grouping_type = 1
        budget.text_includes = request.POST.get('include_strings')
        budget.text_excludes = request.POST.get('exclude_strings')
    else:
        budget.grouping_type = 2

    if request.POST.get('time_period') == 'monthly':
        budget.is_monthly = True
    else:
        budget.is_monthly = False
        flight_dates_input = request.POST.get('flight_dates').split(' - ')
        start_date_comps = flight_dates_input[0].split('/')
        end_date_comps = flight_dates_input[1].split('/')

        start_date = datetime(int(start_date_comps[2]), int(start_date_comps[0]), int(start_date_comps[1]))
        end_date = datetime(int(end_date_comps[2]), int(end_date_comps[0]), int(end_date_comps[1]), 23, 59, 59)

        budget.start_date = start_date
        budget.end_date = end_date

    budget.save()

    return redirect('/budget/client/' + str(account.id) + '/beta')


@login_required
def update_exclusions(request):
    """
    Updates the exclusion list for a client
    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request type')

    account = get_object_or_404(Client, id=request.POST.get('account_id'))
    member = request.user.member

    if account not in member.accounts and not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to do this')

    exclusions, created = CampaignExclusions.objects.get_or_create(account=account)

    campaign_ids = request.POST.getlist('campaigns')

    aw_cmps = []
    fb_cmps = []
    bing_cmps = []

    # We don't know which id is from which platform, so we have to try all 3
    for campaign_id in campaign_ids:
        try:
            aw_cmp = Campaign.objects.get(campaign_id=campaign_id)
            aw_cmps.append(aw_cmp)
        except Campaign.DoesNotExist:
            pass

        try:
            bing_cmp = BingCampaign.objects.get(campaign_id=campaign_id)
            bing_cmps.append(bing_cmp)
        except BingCampaign.DoesNotExist:
            pass

        try:
            fb_cmp = FacebookCampaign.objects.get(campaign_id=campaign_id)
            fb_cmps.append(fb_cmp)
        except FacebookCampaign.DoesNotExist:
            pass

    exclusions.aw_campaigns.set(aw_cmps)
    exclusions.fb_campaigns.set(fb_cmps)
    exclusions.bing_campaigns.set(bing_cmps)

    return redirect('/budget/client/' + str(account.id) + '/beta')
