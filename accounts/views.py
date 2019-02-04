# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from adwords_dashboard.models import DependentAccount
from bing_dashboard.models import BingAccounts
from facebook_dashboard.models import FacebookAccount
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
@xframe_options_exempt
def adwords_accounts(request):
    if request.method == 'POST':
        acc_id = request.POST['id']
        try:
            acc = DependentAccount.objects.get(dependent_account_id=acc_id)
            currentStatus = acc.blacklisted
            acc.blacklisted = not currentStatus
            response = {'status': 'active'} if not acc.blacklisted else {'status': 'inactive'}
            acc.save()
            blacklisted = DependentAccount.objects.filter(blacklisted=True).count()
            whitelisted = DependentAccount.objects.filter(blacklisted=False).count()
            response['whitelisted'] = whitelisted
            response['blacklisted'] = blacklisted
            return JsonResponse(response)
        except:
            raise Http404

    blacklisted = DependentAccount.objects.filter(blacklisted=True).count()
    whitelisted = DependentAccount.objects.filter(blacklisted=False).count()
    protected = DependentAccount.objects.filter(protected=True).count()
    accounts = DependentAccount.objects.all()
    context = {
        'whitelisted': whitelisted,
        'blacklisted': blacklisted,
        'protected': protected,
        'accounts': accounts,
    }
    return render(request, "accounts/adwords.html", context)


@login_required
@xframe_options_exempt
def bing_accounts(request):
    if request.method == 'POST':
        acc_id = request.POST['id']
        try:
            acc = BingAccounts.objects.get(account_id=acc_id)
            currentStatus = acc.blacklisted
            acc.blacklisted = not currentStatus
            response = {'status': 'active'} if not acc.blacklisted else {'status': 'inactive'}
            acc.save()
            blacklisted = BingAccounts.objects.filter(blacklisted=True).count()
            whitelisted = BingAccounts.objects.filter(blacklisted=False).count()
            response['whitelisted'] = whitelisted
            response['blacklisted'] = blacklisted
            return JsonResponse(response)
        except:
            raise Http404

    blacklisted = BingAccounts.objects.filter(blacklisted=True).count()
    whitelisted = BingAccounts.objects.filter(blacklisted=False).count()
    protected = BingAccounts.objects.filter(protected=True).count()
    accounts = BingAccounts.objects.all()
    context = {
        'whitelisted': whitelisted,
        'blacklisted': blacklisted,
        'protected': protected,
        'accounts': accounts,
    }
    return render(request, "accounts/bing.html", context)


@login_required
@xframe_options_exempt
def facebook_accounts(request):
    if request.method == 'POST':
        acc_id = request.POST['id']
        try:
            acc = FacebookAccount.objects.get(account_id=acc_id)
            currentStatus = acc.blacklisted
            acc.blacklisted = not currentStatus
            response = {'status': 'active'} if not acc.blacklisted else {'status': 'inactive'}
            acc.save()
            blacklisted = FacebookAccount.objects.filter(blacklisted=True).count()
            whitelisted = FacebookAccount.objects.filter(blacklisted=False).count()
            response['whitelisted'] = whitelisted
            response['blacklisted'] = blacklisted
            return JsonResponse(response)
        except:
            raise Http404

    blacklisted = FacebookAccount.objects.filter(blacklisted=True).count()
    whitelisted = FacebookAccount.objects.filter(blacklisted=False).count()
    protected = FacebookAccount.objects.filter(protected=True).count()
    accounts = FacebookAccount.objects.all()
    context = {
        'whitelisted': whitelisted,
        'blacklisted': blacklisted,
        'protected': protected,
        'accounts': accounts,
    }
    return render(request, "accounts/facebook.html", context)


# to rewrite
@login_required
@xframe_options_exempt
def change_protected(request):
    if request.method == 'POST':

        acc_id = request.POST['id']
        platform = request.POST['platform']

        if platform == 'aw':
            acc = DependentAccount.objects.get(dependent_account_id=acc_id)
            isprotected = acc.protected
            acc.protected = not isprotected
            response = {'protected': 'true'} if not isprotected else {'protected': 'false'}
            acc.save()
            protected = DependentAccount.objects.filter(protected=True).count()
            response['protected'] = protected
            response['account'] = acc.dependent_account_name
            return JsonResponse(response)

        elif platform == 'bing':
            acc = BingAccounts.objects.get(account_id=acc_id)
            isprotected = acc.protected
            acc.protected = not isprotected
            response = {'protected': 'true'} if not isprotected else {'protected': 'false'}
            acc.save()
            protected = BingAccounts.objects.filter(protected=True).count()
            response['protected'] = protected
            response['account'] = acc.account_name
            return JsonResponse(response)

        elif platform == 'fb':
            acc = FacebookAccount.objects.get(account_id=acc_id)
            isprotected = acc.protected
            acc.protected = not isprotected
            response = {'protected': 'true'} if not isprotected else {'protected': 'false'}
            acc.save()
            protected = FacebookAccount.objects.filter(protected=True).count()
            response['protected'] = protected
            response['account'] = acc.account_name
            return JsonResponse(response)
