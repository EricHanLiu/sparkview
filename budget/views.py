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
        budget = request.POST.get('client_budget')
        adwords_accounts = request.POST.getlist('adwords')
        bing_accounts = request.POST.getlist('bing')

        for a in adwords_accounts:
            aw_acc = DependentAccount.objects.get(dependent_account_name=a)
            aw.append(aw_acc)

        for b in bing_accounts:
            bing_acc = BingAccounts.objects.get(account_name=b)
            bng.append(bing_acc)

        new_client = Client.objects.create(client_name=name, budget=budget)

        for acc in aw:
            new_client.adwords.add(acc)
            new_client.save()
            print('Added to new client ' + acc.dependent_account_name)

        for bacc in bng:
            new_client.bing.add(bacc)
            new_client.save()
            print('Added to new client ' + bacc.account_name)

        aw = []
        bng = []

        context = {}
        # facebook_accounts = request.POST.getlist('facebook')
        return JsonResponse(context)

@login_required
@xframe_options_exempt
def client_details(request, client_id):

    if request.method == 'GET':
        try:
            client = Client.objects.get(id=client_id)
            print(client.bing)
            context = {}
            context['client_data'] = client
            return render(request, 'budget/view_client.html', context)
        except ValueError:
            raise Http404