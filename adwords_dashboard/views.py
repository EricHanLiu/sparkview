# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect

from adwords_dashboard.models import DependentAccount, Performance, CampaignStat
from adwords_dashboard.models import Label, Alert
from celery.result import AsyncResult
from tasks.adwords_tasks import  test_task

# from decorators import cache_on_auth

# Create your views here.
@login_required
def index(request):
    return redirect(adwords_dashboard)

@login_required
def adwords_dashboard(request):

    user = request.user
    items = []
    accounts = DependentAccount.objects.filter(blacklisted=False)
    for account in accounts:
        item = {}
        query = Performance.objects.filter(account=account.pk, performance_type='ACCOUNT')
        item['account'] = account
        item['labels'] = Label.objects.filter(accounts=account, label_type='ACCOUNT')
        item['metadata'] = query[0].metadata if query else {}
        items.append(item)

    if user.is_authenticated():
        return render(request, 'adwords/dashboard.html', {'items': items})
    else:
        return render(request, 'login/login.html')

@login_required
def account_anomalies(request, account_id):

    if request.method == 'GET':

        account = DependentAccount.objects.get(dependent_account_id=account_id)

        anomalies = Performance.objects.filter(account=account,
                                               performance_type='CAMPAIGN')

        campaigns = []

        for cmp in anomalies:
            campaign = {}
            campaign['id'] = cmp.campaign_id
            campaign['name'] = cmp.campaign_name
            campaign['cpc'] = cmp.cpc
            campaign['clicks'] = cmp.clicks
            campaign['impressions'] = cmp.impressions
            campaign['cost'] = cmp.cost
            campaign['conversions'] = cmp.conversions
            campaign['cost_per_conversions'] = cmp.cost_per_conversions
            campaign['ctr'] = cmp.ctr
            campaign['search_impr_share'] = cmp.search_impr_share
            campaigns.append(campaign)

        context = {
            'account': account,
            'campaigns': campaigns
        }

        return render(request, 'adwords/account_anomalies.html', context)

    elif request.method == 'POST':
        data = request.POST
        print(data['fmin'], data['smin'])


        response = {}
        return JsonResponse(response)

@login_required
def campaign_404(request, acc_id):

    current_account = DependentAccount.objects.get(dependent_account_id=acc_id)

    try:

        current_campaigns = CampaignStat.objects.all().filter(dependent_account_id=acc_id)
    except:
        current_campaigns = {}
        current_campaigns['error'] = "No campaigns found"
    context = {
        'account': current_account,
        'campaigns': current_campaigns
        }
    return render(request, "adwords/404_list.html", context)


@login_required
def account_alerts(request, account_id):
    # alert_types = ['DISAPPROVED_AD']

    account = DependentAccount.objects.get(dependent_account_id=account_id)
    alerts = Alert.objects.filter(dependent_account_id=account_id)
    context = {
        'alerts': alerts,
        'account': account
    }
    return render(request, 'adwords/account_alerts.html', context)

@login_required
def test_view(request):
    if request.method == 'GET' and 'task_id' in request.GET:
        taskt = AsyncResult(request.GET['task_id'])

        if taskt.state == 'SUCCESS':
            return JsonResponse(
                {
                    'tresult':taskt.result,
                    'tstate': taskt.state
                 })
        return JsonResponse({'tid': taskt.id, 'tstate': taskt.state})

    if request.method == 'POST':
        t_in_prog = test_task.delay()
        return JsonResponse({'tid': t_in_prog.id, 'tstate': t_in_prog.state})
    return JsonResponse({}, status=400)
