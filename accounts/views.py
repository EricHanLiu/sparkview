# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import Http404, JsonResponse
from django.shortcuts import render
from adwords_dashboard import models

# Create your views here.

def adwords_accounts(request):

    if request.method == 'POST':
        acc_id = request.POST['id']
        try:
            acc = models.DependentAccount.objects.get(dependent_account_id=acc_id)
            currentStatus = acc.blacklisted
            acc.blacklisted = not currentStatus
            response = {'status':'active'} if not acc.blacklisted else {'status': 'inactive'}
            acc.save()
            blacklisted = models.DependentAccount.objects.filter(blacklisted=True).count()
            whitelisted = models.DependentAccount.objects.filter(blacklisted=False).count()
            response['whitelisted'] = whitelisted
            response['blacklisted'] = blacklisted
            return JsonResponse(response)
        except:
            raise Http404


    blacklisted = models.DependentAccount.objects.filter(blacklisted=True).count()
    whitelisted = models.DependentAccount.objects.filter(blacklisted=False).count()
    accounts = models.DependentAccount.objects.all()
    context = {
        'whitelisted': whitelisted,
        'blacklisted': blacklisted,
        'accounts': accounts,
    }
    return render(request, "accounts/adwords.html", context)

def bing_accounts(request):
    context = {}
    return render(request, "accounts/bing.html", context)
