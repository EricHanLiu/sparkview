from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from .auth import BingAuth
from bingads import ServiceClient
from bingads.v11.reporting import *
from bing_dashboard import models
from .auth_helper import *

# Create your views here.
@login_required
def index(request):
    return request(bing_dashboard)

@login_required
@xframe_options_exempt
def bing_dashboard(request):

    items = []
    accounts = models.BingAccounts.objects.filter(blacklisted=False)
    for account in accounts:
        item = {}
        item['account'] = account
        query = models.BingAnomalies.objects.filter(account=account.pk, performance_type='ACCOUNT')
        item['clicks'] = query[0].clicks if query else 0
        item['impressions'] = query[0].impressions if query else 0
        item['ctr'] = query[0].ctr if query else 0
        item['cpc'] = query[0].cpc if query else 0
        item['conversions'] = query[0].conversions if query else 0
        item['cost'] = query[0].cost if query else 0
        item['cost_conv'] = query[0].cost_per_conversions if query else 0
        item['impr_share'] = query[0].search_impr_share if query else 0
        items.append(item)
    return render(request, 'bing/dashboard.html', {'items': items})

def campaign_anomalies(request):
    return HttpResponse('Ok')


class BingSingin(View):

    def get(self, request, *args, **kwargs):

        current_user = request.user

        if current_user.is_authenticated():
            bing_auth = BingAuth(username=current_user.username)
            return JsonResponse({'url': bing_auth.get_auth_url()})

        return HttpResponse('Auth required', status=401)


class BingExchange(View):

    def get(self, request, *args, **kwargs):
        url = request.build_absolute_uri()
        current_user = request.user

        if 'code' not in url:
            return HttpResponse('Missing URI', status=403)

        if current_user.is_authenticated():
            bing_auth = BingAuth(username=current_user.username)
            creds = bing_auth.authenticate(response_uri=url)
            if creds:
                return JsonResponse({'message': 'Registration successful!'})
            else:
                return HttpResponse('Ups! Something went wrong', status=403)

        return HttpResponse('Unauthorized.')


class AuthenticateBing(View):

    def get(self, request, *args, **kwargs):
        current_user = request.user
        if current_user.is_authenticated():

            bing_auth = BingAuth(username=current_user.username)
            creds = bing_auth.get_creds()


            return JsonResponse({
                'refresh_token': creds.refresh_token,
                'access_token': creds.access_token})



class TestBing(View):

    @xframe_options_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(TestBing, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        data = {}
        account_list = []

        auth = BingAuth().get_auth()

        customer_service = ServiceClient(
            service='CustomerManagementService',
            authorization_data=auth,
            environment='production',
            version=11,
        )

        user = customer_service.GetUser(UserId=None).User
        user_id = user.Id

        paging={
            'Index': 0,
            'Size': 500
        }

        predicates={
            'Predicate': [
                {
                    'Field': 'UserId',
                    'Operator': 'Equals',
                    'Value': user.Id,
                },
            ]
        }

        search_accounts_request={
            'PageInfo': paging,
            'Predicates': predicates
        }

        accounts = customer_service.SearchAccounts(
            PageInfo=paging,
            Predicates=predicates
            )

        for account in accounts['Account']:
            customer_service.GetAccount(AccountId=account.Id)
            data['name'] = account['Name']
            data['account_id'] = account['Id']
            account_list.append(data)
            data = {}

        print('data appended')
        return HttpResponse(account_list)
