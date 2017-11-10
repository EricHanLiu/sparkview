# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect

# from decorators import cache_on_auth

# Create your views here.

@login_required
def index(request):
    return redirect(adwords_dashboard)

@login_required
def adwords_dashboard(request):
    return render(request, 'adwords_dashboard/index.html', {})