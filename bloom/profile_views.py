from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from adwords_dashboard.models import DependentAccount, Profile
from bing_dashboard.models import BingAccounts
import json


def view_profile(request):

    user = request.user

    if request.method == 'GET':

        bing_accounts = BingAccounts.objects.filter(assigned=False)
        adwords_accounts = DependentAccount.objects.filter(assigned=False)
        user_profile = Profile.objects.get(user=user)

        context = {
            'bing': bing_accounts,
            'adwords': adwords_accounts,
            'user_profile': user_profile

        }
        return render(request, 'profile.html', context)

    elif request.method == 'POST':

        adwords = request.POST.getlist('adwords')
        bing = request.POST.getlist('bing')
        email = request.POST.get('user-email')

        if email == user.email:
            pass
        else:
            user.email = email
            user.save()

        profile = Profile.objects.get(user=request.user)

        if adwords:
            for a in adwords:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                aw_acc.assigned = True
                aw_acc.assigned_to = user
                profile.adwords.add(aw_acc)
                aw_acc.save()
                profile.save()

        if bing:
            for b in bing:
                bing_acc = BingAccounts.objects.get(account_id=b)
                bing_acc.assigned = True
                bing_acc.assigned_to = user
                profile.bing.add(bing_acc)
                bing_acc.save()
                profile.save()

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)

def remove_acc_profile(request):

    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        acc_id = data['acc_id']

        try:
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned = False
            account.assigned_to = None
            profile.adwords.remove(account)
            account.save()
            profile.save()

        except ObjectDoesNotExist:
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned = False
            account.assigned_to = None
            profile.bing.remove(account)
            account.save()
            profile.save()

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)
