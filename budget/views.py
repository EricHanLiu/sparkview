# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from adwords_dashboard.models import DependentAccount
from bing_dashboard.models import BingAccounts
import calendar
from datetime import datetime
# from dashboard.decorators import cache_on_auth



# Create your views here.
@login_required
@xframe_options_exempt
def index(request):
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
                item = {}
                item['account'] = acc
                items.append(item)
            return render(request, 'budget/adwords_budget.html', {'items' : items})
        except ValueError:
            raise Http404

    elif request.method == 'POST':
        try:
            account = DependentAccount.objects.get(dependent_account_id=request.POST['acc_id'])
            desired_spend = request.POST['desired_spend']
            account.desired_spend = desired_spend
            account.dependent_OVU = (float(account.current_spend) / (float(account.desired_spend) / days * now.day)) * 100
            account.save()
            context = {}
            context['error'] = 'OK'
            context['OVU'] = account.dependent_OVU
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
                item = {}
                item['account'] = acc
                items.append(item)
            return render(request, 'budget/bing_budget.html', {'items' : items})
        except ValueError:
            raise Http404

    elif request.method == 'POST':
        try:
            account = BingAccounts.objects.get(account_id=request.POST['acc_id'])
            desired_spend = request.POST['desired_spend']
            account.desired_spend = desired_spend
            account.account_ovu = int(float(account.current_spend) / float(account.desired_spend) * float(100))
            account.save()
            context = {}
            context['error'] = 'OK'
            context['OVU'] = account.account_ovu
            return JsonResponse(context)
        except ValueError:
            raise Http404
