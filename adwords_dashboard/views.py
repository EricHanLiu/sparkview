# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect

from adwords_dashboard.models import DependentAccount, Performance, CampaignStat
from adwords_dashboard.models import Label, Alert

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
        item['clicks'] = query[0].clicks if query else 0
        item['impressions'] = query[0].impressions if query else 0
        item['ctr'] = query[0].ctr if query else 0
        item['cpc'] = query[0].cpc if query else 0
        item['conversions'] = query[0].conversions if query else 0
        item['cost'] = query[0].cost if query else 0
        item['cost_per_conversions'] = query[0].cost_per_conversions if query else 0
        item['search_impr_share'] = query[0].search_impr_share if query else 0
        item['disapproved_ads'] = Alert.objects.filter(dependent_account_id=account.dependent_account_id,
                                                       alert_type='DISAPPROVED_AD').count()
        items.append(item)

    if user.is_authenticated():
        return render(request, 'adwords/dashboard.html', {'items': items})
    else:
        return render(request, 'login/login.html')

@login_required
def campaign_anomalies(request, account_id):

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

    return render(request, 'adwords/campaign_anomalies.html', context)

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