from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from user_management.models import Member
import json


def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            try:
                member = Member.objects.get(user=request.user)
            except Member.DoesNotExist:
                return redirect('/user_management/profile')
            return redirect('/user_management/members/' + str(member.id) + '/dashboard')
        return redirect('/user_management/profile')

    return render(request, 'login/login.html')


def bloom_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            response = {}
            request_body = request.body
            if isinstance(request_body, bytes):
                request_body = request_body.decode(encoding='utf-8')
            login_data = json.loads(request_body)
            username = login_data['username']
            password = login_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                response['success'] = 'Login successful'
                return JsonResponse(response)
            else:
                response['error'] = 'Invalid username or password.'
                return JsonResponse(response)

    return redirect("/")


@login_required
def bloom_logout(request):
    logout(request)
    return redirect("/")
