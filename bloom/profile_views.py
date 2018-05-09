from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect, reverse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.views.decorators import staff_member_required
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
        aw_to = DependentAccount.objects.filter(assigned_to=user)
        aw_cm2 = DependentAccount.objects.filter(assigned_cm2=user)
        aw_cm3 = DependentAccount.objects.filter(assigned_cm3=user)
        bing_to = BingAccounts.objects.filter(assigned_to=user)
        bing_cm2 = BingAccounts.objects.filter(assigned_cm2=user)
        bing_cm3 = BingAccounts.objects.filter(assigned_cm3=user)

        context = {
            'adwords': adwords_accounts,
            'bing': bing_accounts,
            'aw_to': aw_to,
            'aw_cm2': aw_cm2,
            'aw_cm3': aw_cm3,
            'bing_to': bing_to,
            'bing_cm2': bing_cm2,
            'bing_cm3': bing_cm3,
            'user_profile': user_profile

        }
        return render(request, 'profile.html', context)

    elif request.method == 'POST':

        adwords = request.POST.getlist('adwords')
        adwords_cm2 = request.POST.getlist('adwords_cm2')
        adwords_cm3 = request.POST.getlist('adwords_cm3')
        bing = request.POST.getlist('bing')
        bing_cm2 = request.POST.getlist('bing_cm2')
        bing_cm3 = request.POST.getlist('bing_cm3')
        email = request.POST.get('user-email')

        if email == user.email:
            pass
        else:
            user.email = email
            user.save()

        profile = Profile.objects.get(user=user)

        if adwords:
            for a in adwords:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                # aw_acc.assigned = True
                aw_acc.assigned_to = user
                # profile.adwords.add(aw_acc)
                aw_acc.save()
                # profile.save()
        if adwords_cm2:
            for a in adwords_cm2:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                aw_acc.assigned_cm2 = user
                aw_acc.save()
        if adwords_cm3:
            for a in adwords_cm3:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                aw_acc.assigned_cm3 = user
                aw_acc.save()

        if bing:
            for b in bing:
                bing_acc = BingAccounts.objects.get(account_id=b)
                # bing_acc.assigned = True
                bing_acc.assigned_to = user
                # profile.bing.add(bing_acc)
                bing_acc.save()
                # profile.save()

        if bing_cm2:
            for b in bing_cm2:
                bing_acc = BingAccounts.objects.get(account_id=b)
                bing_acc.assigned_cm2 = user
                bing_acc.save()

        if bing_cm3:
            for b in bing_cm3:
                bing_acc = BingAccounts.objects.get(account_id=b)
                bing_acc.assigned_cm3 = user
                bing_acc.save()

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
        level = data['cm']


        if level == 'cm':
            try:
                account = DependentAccount.objects.get(dependent_account_id=acc_id)
                # account.assigned = False
                account.assigned_to = None
                profile.adwords.remove(account)
                account.save()
                profile.save()

            except ObjectDoesNotExist:
                account = BingAccounts.objects.get(account_id=acc_id)
                # account.assigned = False
                account.assigned_to = None
                profile.bing.remove(account)
                account.save()
                profile.save()

        if level == 'cm2':
            try:
                account = DependentAccount.objects.get(dependent_account_id=acc_id)
                account.assigned_cm2 = None
                account.save()
            except ObjectDoesNotExist:
                account = BingAccounts.objects.get(account_id=acc_id)
                account.assigned_cm2 = None
                account.save()

        if level == 'cm3':
            try:
                account = DependentAccount.objects.get(dependent_account_id=acc_id)
                account.assigned_cm3 = None
                account.save()
            except ObjectDoesNotExist:
                account = BingAccounts.objects.get(account_id=acc_id)
                account.assigned_cm3 = None
                account.save()

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)

def change_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.add_message(request, messages.SUCCESS, 'Sucessfully changed password.')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

@staff_member_required
def user_list(request):

    if request.method == 'GET':

        details = []
        users = User.objects.all()
        adwords = DependentAccount.objects.all()
        bing = BingAccounts.objects.all()

        for user in users:
            detail ={
                'user': user,
                'aw_to': DependentAccount.objects.filter(assigned_to=user),
                'aw_cm2': DependentAccount.objects.filter(assigned_cm2=user),
                'aw_cm3': DependentAccount.objects.filter(assigned_cm3=user),
                'bing_to': BingAccounts.objects.filter(assigned_to=user),
                'bing_cm2': BingAccounts.objects.filter(assigned_cm2=user),
                'bing_cm3': BingAccounts.objects.filter(assigned_cm3=user)
            }
            details.append(detail)

        context = {
            'details': details,
            'adwords': adwords,
            'bing': bing
        }

        return render(request, 'users.html', context)

    elif request.method == 'POST':

        uid = request.POST.get('uid')
        adwords = request.POST.getlist('adwords_cm')
        adwords_cm2 = request.POST.getlist('adwords_cm2')
        adwords_cm3 = request.POST.getlist('adwords_cm3')
        bing = request.POST.getlist('bing_cm')
        bing_cm2 = request.POST.getlist('bing_cm2')
        bing_cm3 = request.POST.getlist('bing_cm3')

        user = User.objects.get(id=uid)

        if adwords:
            for a in adwords:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                aw_acc.assigned_to = user
                aw_acc.save()

        if adwords_cm2:
            for a in adwords_cm2:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                aw_acc.assigned_cm2 = user
                aw_acc.save()
        if adwords_cm3:
            for a in adwords_cm3:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                aw_acc.assigned_cm3 = user
                aw_acc.save()

        if bing:
            for b in bing:
                bing_acc = BingAccounts.objects.get(account_id=b)
                bing_acc.assigned_to = user
                bing_acc.save()

        if bing_cm2:
            for b in bing_cm2:
                bing_acc = BingAccounts.objects.get(account_id=b)
                bing_acc.assigned_cm2 = user
                bing_acc.save()

        if bing_cm3:
            for b in bing_cm3:
                bing_acc = BingAccounts.objects.get(account_id=b)
                bing_acc.assigned_cm3 = user
                bing_acc.save()

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)

def remove_user_accounts(request):

    data = json.loads(request.body.decode('utf-8'))
    acc_id = data['acc_id']
    level = data['cm']

    if level == 'cm':
        try:
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned_to = None
            account.save()
            # account.assigned = False
            # profile.adwords.remove(account)
            # profile.save()

        except ObjectDoesNotExist:
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned_to = None
            account.save()
            # account.assigned = False
            # profile.bing.remove(account)
            # profile.save()

    if level == 'cm2':
        try:
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned_cm2 = None
            account.save()
        except ObjectDoesNotExist:
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned_cm2 = None
            account.save()

    if level == 'cm3':
        try:
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned_cm3 = None
            account.save()
        except ObjectDoesNotExist:
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned_cm3 = None
            account.save()

    context = {
        'error': 'OK'
    }
    return JsonResponse(context)
