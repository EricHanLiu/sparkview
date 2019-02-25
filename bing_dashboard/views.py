from bing_dashboard.models import BingAccounts, BingAnomalies, BingAlerts
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required
from .auth import BingAuth


# Create your views here.
@login_required
def index(request):
    return request(bing_dashboard)


@login_required
@xframe_options_exempt
def bing_dashboard(request):
    items = []
    accounts = BingAccounts.objects.filter(blacklisted=False)

    for account in accounts:
        item = {}
        item['account'] = account
        query = BingAnomalies.objects.filter(account=account.pk, performance_type='ACCOUNT')
        item['metadata'] = query[0].metadata if query else {}
        item['clicks'] = query[0].clicks if query else 0
        item['impressions'] = query[0].impressions if query else 0
        item['ctr'] = query[0].ctr if query else 0
        item['cpc'] = query[0].cpc if query else 0
        item['conversions'] = query[0].conversions if query else 0
        item['cost'] = query[0].cost if query else 0
        item['cost_conv'] = query[0].cost_per_conversions if query else 0
        item['impr_share'] = query[0].search_impr_share if query else 0
        item['disapproved_ads'] = BingAlerts.objects.filter(account=account).count()
        items.append(item)
    return render(request, 'bing/dashboard.html', {'items': items})


def campaign_anomalies(request, account_id):
    account = BingAccounts.objects.get(account_id=account_id)

    anomalies = BingAnomalies.objects.filter(account=account,
                                             performance_type='CAMPAIGN')

    campaigns = []

    for cmp in anomalies:
        campaign = {}
        campaign['id'] = cmp.campaign_id
        campaign['name'] = cmp.campaign_name
        campaign['cpc'] = cmp.cpc
        campaign['clicks'] = cmp.clicks
        campaign['impressions'] = cmp.impressions
        campaign['cost'] = cmp.cost
        campaign['conversions'] = cmp.conversions
        campaign['cost_per_conversions'] = cmp.cost_per_conversions
        campaign['ctr'] = cmp.ctr
        campaign['search_impr_share'] = cmp.search_impr_share
        campaign['metadata'] = cmp.metadata
        campaigns.append(campaign)

    context = {
        'account': account,
        'campaigns': campaigns
    }

    return render(request, 'bing/campaign_anomalies.html', context)


@login_required
def account_alerts(request, account_id):
    # alert_types = ['DISAPPROVED_AD']

    account = BingAccounts.objects.get(account_id=account_id)
    alerts = BingAlerts.objects.filter(account=account)

    context = {
        'alerts': alerts,
        'account': account
    }
    return render(request, 'bing/account_alerts.html', context)


class BingSingin(View):

    def get(self, request, *args, **kwargs):
        current_user = request.user

        if current_user.is_authenticated:
            bing_auth = BingAuth(username=current_user.username)
            return JsonResponse({'url': bing_auth.get_auth_url()})

        return HttpResponse('Auth required', status=401)


class BingExchange(View):

    def get(self, request, *args, **kwargs):
        url = request.build_absolute_uri()
        current_user = request.user

        if 'code' not in url:
            return HttpResponse('Missing URI', status=403)

        if current_user.is_authenticated:
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
        if current_user.is_authenticated:
            bing_auth = BingAuth(username=current_user.username)
            creds = bing_auth.get_creds()

            return JsonResponse({
                'refresh_token': creds.refresh_token,
                'access_token': creds.access_token})
