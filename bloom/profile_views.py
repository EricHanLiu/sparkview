from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core import serializers
from adwords_dashboard.models import DependentAccount, Profile
from bing_dashboard.models import BingAccounts
from facebook_dashboard.models import FacebookAccount
from budget.models import Client
from user_management.models import Member
from social_django.models import UserSocialAuth
import json


def view_profile(request):
    user = request.user

    if request.method == 'GET':

        adwords_accounts = DependentAccount.objects.all()
        bing_accounts = BingAccounts.objects.all()
        facebook_accounts = FacebookAccount.objects.all()
        user_profile = Profile.objects.get(user=user)
        aw_to = DependentAccount.objects.filter(assigned_to=user)
        aw_cm2 = DependentAccount.objects.filter(assigned_cm2=user)
        aw_cm3 = DependentAccount.objects.filter(assigned_cm3=user)
        aw_am = DependentAccount.objects.filter(assigned_am=user)
        bing_to = BingAccounts.objects.filter(assigned_to=user)
        bing_cm2 = BingAccounts.objects.filter(assigned_cm2=user)
        bing_cm3 = BingAccounts.objects.filter(assigned_cm3=user)
        bing_am = BingAccounts.objects.filter(assigned_am=user)
        fb_to = FacebookAccount.objects.filter(assigned_to=user)
        fb_cm2 = FacebookAccount.objects.filter(assigned_cm2=user)
        fb_cm3 = FacebookAccount.objects.filter(assigned_cm3=user)
        fb_am = FacebookAccount.objects.filter(assigned_am=user)

        try:
            google_login = user.social_auth.get(provider='google-oauth2')
        except UserSocialAuth.DoesNotExist:
            google_login = None

        context = {
            'adwords': adwords_accounts,
            'google_login': google_login,
            'bing': bing_accounts,
            'facebook': facebook_accounts,
            'aw_to': aw_to,
            'aw_cm2': aw_cm2,
            'aw_cm3': aw_cm3,
            'bing_to': bing_to,
            'bing_cm2': bing_cm2,
            'bing_cm3': bing_cm3,
            'fb_to': fb_to,
            'fb_cm2': fb_cm2,
            'fb_cm3': fb_cm3,
            'user_profile': user_profile

        }
        return render(request, 'profile.html', context)

    elif request.method == 'POST':

        email = request.POST.get('user-email')

        if email == user.email:
            pass
        else:
            user.email = email
            user.save()

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
        channel = data['channel']

        if channel == 'adwords':
            if level == 'cm':
                account = DependentAccount.objects.get(dependent_account_id=acc_id)
                account.assigned_to = None
                profile.adwords.remove(account)
                account.save()
                profile.save()

            if level == 'cm2':
                account = DependentAccount.objects.get(dependent_account_id=acc_id)
                account.assigned_cm2 = None
                account.save()

            if level == 'cm3':
                account = DependentAccount.objects.get(dependent_account_id=acc_id)
                account.assigned_cm3 = None
                account.save()

            context = {
                'account_name': account.dependent_account_name,
                'account_id': account.dependent_account_id,
                'channel': channel
            }

        if channel == 'bing':
            if level == 'cm':
                account = BingAccounts.objects.get(account_id=acc_id)
                account.assigned_to = None
                profile.bing.remove(account)
                account.save()
                profile.save()

            if level == 'cm2':
                account = BingAccounts.objects.get(account_id=acc_id)
                account.assigned_cm2 = None
                account.save()

            if level == 'cm3':
                account = BingAccounts.objects.get(account_id=acc_id)
                account.assigned_cm3 = None
                account.save()

            context = {
                'account_name': account.account_name,
                'account_id': account.account_id,
                'channel': channel
            }

        if channel == 'facebook':
            if level == 'cm':
                account = FacebookAccount.objects.get(account_id=acc_id)
                account.assigned_to = None
                account.save()

            if level == 'cm2':
                account = FacebookAccount.objects.get(account_id=acc_id)
                account.assigned_cm2 = None
                account.save()

            if level == 'cm3':
                account = FacebookAccount.objects.get(account_id=acc_id)
                account.assigned_cm3 = None
                account.save()

            context = {
                'account_name': account.account_name,
                'account_id': account.account_id,
                'channel': channel
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
        facebook = FacebookAccount.objects.all()

        for user in users:
            detail = {
                'user': user,
                'aw_to': DependentAccount.objects.filter(assigned_to=user),
                'aw_cm2': DependentAccount.objects.filter(assigned_cm2=user),
                'aw_cm3': DependentAccount.objects.filter(assigned_cm3=user),
                'aw_am': DependentAccount.objects.filter(assigned_am=user),
                'bing_to': BingAccounts.objects.filter(assigned_to=user),
                'bing_cm2': BingAccounts.objects.filter(assigned_cm2=user),
                'bing_cm3': BingAccounts.objects.filter(assigned_cm3=user),
                'bing_am': BingAccounts.objects.filter(assigned_am=user),
                'facebook_to': FacebookAccount.objects.filter(assigned_to=user),
                'facebook_cm2': FacebookAccount.objects.filter(assigned_cm2=user),
                'facebook_cm3': FacebookAccount.objects.filter(assigned_cm3=user),
                'facebook_am': FacebookAccount.objects.filter(assigned_am=user),
            }
            details.append(detail)

        context = {
            'details': details,
            'adwords': adwords,
            'bing': bing,
            'facebook': facebook
        }

        return render(request, 'users.html', context)

    elif request.method == 'POST':

        uid = request.POST.get('uid')
        adwords = request.POST.getlist('adwords_cm')
        adwords_cm2 = request.POST.getlist('adwords_cm2')
        adwords_cm3 = request.POST.getlist('adwords_cm3')
        adwords_am = request.POST.getlist('adwords_am')
        bing = request.POST.getlist('bing_cm')
        bing_cm2 = request.POST.getlist('bing_cm2')
        bing_cm3 = request.POST.getlist('bing_cm3')
        bing_am = request.POST.getlist('bing_am')
        facebook = request.POST.getlist('facebook')
        facebook_cm2 = request.POST.getlist('facebook_cm2')
        facebook_cm3 = request.POST.getlist('facebook_cm3')
        facebook_am = request.POST.getlist('facebook_am')
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

        if adwords_am:
            for a in adwords_am:
                aw_acc = DependentAccount.objects.get(dependent_account_id=a)
                aw_acc.assigned_am = user
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

        if bing_am:
            for b in bing_am:
                bing_acc = BingAccounts.objects.get(account_id=b)
                bing_acc.assigned_am = user
                bing_acc.save()

        if facebook:
            for f in facebook:
                fb_acc = FacebookAccount.objects.get(account_id=f)
                fb_acc.assigned_to = user
                fb_acc.save()

        if facebook_cm2:
            for f in facebook_cm2:
                fb_acc = FacebookAccount.objects.get(account_id=f)
                fb_acc.assigned_cm2 = user
                fb_acc.save()

        if facebook_cm3:
            for f in facebook_cm3:
                fb_acc = FacebookAccount.objects.get(account_id=f)
                fb_acc.assigned_cm3 = user
                fb_acc.save()

        if facebook_am:
            for f in facebook_am:
                fb_acc = FacebookAccount.objects.get(account_id=f)
                fb_acc.assigned_am = user
                fb_acc.save()

        context = {
            'error': 'OK'
        }
        return JsonResponse(context)


def remove_user_accounts(request):
    data = json.loads(request.body.decode('utf-8'))
    acc_id = data['acc_id']
    level = data['cm']
    platform = data['platform']

    if platform == 'adwords':
        if level == 'am':
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned_am = None
            account.save()

        if level == 'cm':
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned_to = None
            account.save()

        if level == 'cm2':
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned_cm2 = None
            account.save()

        if level == 'cm3':
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.assigned_cm3 = None
            account.save()

    if platform == 'bing':
        if level == 'am':
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned_am = None
            account.save()

        if level == 'cm':
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned_cm2 = None
            account.save()

        if level == 'cm2':
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned_cm2 = None
            account.save()

        if level == 'cm3':
            account = BingAccounts.objects.get(account_id=acc_id)
            account.assigned_cm3 = None
            account.save()

    if platform == 'facebook':
        if level == 'am':
            account = FacebookAccount.objects.get(account_id=acc_id)
            account.assigned_am = None
            account.save()

        if level == 'cm':
            account = FacebookAccount.objects.get(account_id=acc_id)
            account.assigned_to = None
            account.save()

        if level == 'cm2':
            account = FacebookAccount.objects.get(account_id=acc_id)
            account.assigned_cm2 = None
            account.save()

        if level == 'cm3':
            account = FacebookAccount.objects.get(account_id=acc_id)
            account.assigned_cm3 = None
            account.save()

    context = {
        'error': 'OK'
    }

    return JsonResponse(context)


def create_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    hashed_password = make_password(password)
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    is_staff = request.POST.get('is_staff')

    is_taken = User.objects.filter(username__iexact=username).exists()

    if is_taken:
        response = {
            'error_message': 'User ' + username + ' already exists.'
        }

    else:
        u = User.objects.create(username=username, password=hashed_password, first_name=first_name, last_name=last_name,
                                email=email)

        if is_staff == 'on':
            u.is_staff = True
            u.save()

        response = {
            'username': username
        }

    return JsonResponse(response)


def delete_user(request):
    data = json.loads(request.body.decode('utf-8'))

    user = User.objects.get(id=data['user_id'])

    response = {
        'username': user.username
    }
    user.delete()

    return JsonResponse(response)


@login_required
def search(request):
    res = []
    query = request.GET.get('query')

    clients = Client.objects.filter(
        Q(client_name__icontains=query)
    )

    users = User.objects.filter(
        Q(username__icontains=query)
    )

    members = None
    if users.count() > 0:
        members = Member.objects.filter(user__in=users)

    for r in clients:
        item = {
            'name': r.client_name,
            'url': '/clients/accounts/' + str(r.id)
        }
        res.append(item)

    if members is not None:
        for u in members:
            item = {
                'username': u.user.get_full_name(),
                'member_url': '/user_management/members/' + str(u.id)
            }
            res.append(item)
    return JsonResponse(res, safe=False)
