# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from adwords_dashboard.models import DependentAccount
from bing_dashboard.models import BingAccounts
from budget.models import Client
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

@login_required
@xframe_options_exempt
def add_client(request):

    aw = []
    bng = []

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
            return render(request, 'budget/clients.html', context)
        except ValueError:
            raise Http404

    elif request.method == 'POST':

        name = request.POST.get('client_name')
        new_client = Client.objects.create(client_name=name)

        adwords_accounts = set(request.POST.getlist('adwords'))
        for a in adwords_accounts:
            print(a)
            aw_acc = DependentAccount.objects.get(dependent_account_name=a)
            # new_client.adwords = aw_acc
            # new_client.save()

        bing_accounts = set(request.POST.getlist('bing'))
        for b in bing_accounts:
            print(b)
            bing_acc = BingAccounts.objects.get(account_name=b)
            new_client.bing = bing_acc
            new_client.save()
            bng.append(bing_acc)


        context = {}
        # facebook_accounts = request.POST.getlist('facebook')
        return JsonResponse(context)