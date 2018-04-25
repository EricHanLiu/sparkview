from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.
@login_required
def index(request):
    return request(facebook_dashboard)

@login_required
@xframe_options_exempt
def facebook_dashboard(request):

    return HttpResponse('GG WP! It works!')