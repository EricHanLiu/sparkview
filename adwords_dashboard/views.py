# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect

from adwords_dashboard.models import DependentAccount, Performance

from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . serializers import AccountSerializer, PerformanceSerializer

# from decorators import cache_on_auth

# Create your views here.
class AdwordsDashboardApi(APIView):
    """Api View for populating adwords datatable"""

    renderer_classes = (JSONRenderer, )

    def get(self, request, format=None):

        accounts = DependentAccount.objects.all()
        performance = Performance.objects.filter(performance_type='ACCOUNT')
        acc_serializer = AccountSerializer(accounts, many=True)
        performance_serializer = PerformanceSerializer(performance, many=True, context={'request': request})

        return Response({'data': performance_serializer.data})


@login_required
def index(request):
    return redirect(adwords_dashboard)

@login_required
def adwords_dashboard(request):

    user = request.user
    items = []
    accounts = DependentAccount.objects.all()
    for account in accounts:
        item = {}
        query = Performance.objects.filter(account=account.pk, performance_type='ACCOUNT')
        item['account'] = account
        item['clicks'] = query[0].clicks if query else 0
        item['impressions'] = query[0].impressions if query else 0
        item['ctr'] = query[0].ctr if query else 0
        item['cpc'] = query[0].cpc if query else 0
        item['conversions'] = query[0].conversions if query else 0
        item['cost'] = query[0].cost if query else 0
        item['cost_per_conversions'] = query[0].cost_per_conversions if query else 0
        item['search_impr_share'] = query[0].search_impr_share if query else 0
        items.append(item)

    if user.is_authenticated():
        return render(request, 'adwords_dashboard/adwords_dashboard.html', {'items': items})
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
        campaign = {}
        campaign['id'] = cmp.campaign_id
        campaign['name'] = cmp.campaign_name
        campaign['cpc'] = cmp.cpc
        campaign['clicks'] = cmp.clicks
        campaign['impressions'] = cmp.impressions
        campaign['cost'] = cmp.cpc
        campaign['conversions'] = cmp.cpc
        campaign['cost_per_conversions'] = cmp.cpc
        campaign['ctr'] = cmp.ctr
        campaign['search_impr_share'] = cmp.search_impr_share
        campaigns.append(campaign)

    context = {
        'account': account,
        'campaigns': campaigns
    }

    return render(request, 'adwords_dashboard/campaign_anomalies.html', context)
