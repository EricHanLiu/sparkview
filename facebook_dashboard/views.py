from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from facebook_dashboard.models import FacebookAccount, FacebookPerformance, FacebookAlert

# Create your views here.
@login_required
def index(request):
    return request(facebook_dashboard)

@login_required
@xframe_options_exempt
def facebook_dashboard(request):

    user = request.user
    items = []
    accounts = FacebookAccount.objects.filter(blacklisted=False)
    for account in accounts:
        item = {}
        query = FacebookPerformance.objects.filter(account=account.pk, performance_type='ACCOUNT')
        item['account'] = account
        # item['404_urls'] = CampaignStat.objects.filter(dependent_account_id=account.dependent_account_id).count()
        # item['labels'] = Label.objects.filter(account_id=account.dependent_account_id, label_type='ACCOUNT')
        item['clicks'] = query[0].clicks if query else 0
        item['impressions'] = query[0].impressions if query else 0
        item['ctr'] = query[0].ctr if query else 0
        item['cpc'] = query[0].cpc if query else 0
        # item['conversions'] = query[0].conversions if query else 0
        item['cost'] = query[0].cost if query else 0
        # item['cost_per_conversions'] = query[0].cost_per_conversions if query else 0
        # item['search_impr_share'] = query[0].search_impr_share if query else 0
        item['disapproved_ads'] = FacebookAlert.objects.filter(account=account,
                                                       alert_type='DISAPPROVED_AD').count()
        items.append(item)

    if user.is_authenticated():
        return render(request, 'facebook/dashboard.html', {'items': items})
    else:
        return render(request, 'login/login.html')



@login_required
def campaign_anomalies(request, account_id):

    account = FacebookAccount.objects.get(account_id=account_id)

    anomalies = FacebookPerformance.objects.filter(account=account,
                                           performance_type='CAMPAIGN')

    campaigns = []

    for cmp in anomalies:
        campaign = {}
        campaign['id'] = cmp.campaign_id
        campaign['name'] = cmp.campaign_name
        campaign['cpc'] = cmp.cpc
        campaign['clicks'] = cmp.clicks
        campaign['impressions'] = cmp.impressions
        campaign['cost'] = cmp.cpc
        # campaign['conversions'] = cmp.cpc
        campaign['cost_per_conversions'] = cmp.cpc
        campaign['ctr'] = cmp.ctr
        # campaign['search_impr_share'] = cmp.search_impr_share
        campaigns.append(campaign)

    context = {
        'account': account,
        'campaigns': campaigns
    }

    return render(request, 'facebook/campaign_anomalies.html', context)


@login_required
def account_alerts(request, account_id):
    alert_type = 'DISAPPROVED_AD'

    account = FacebookAccount.objects.get(account_id=account_id)
    alerts = FacebookAlert.objects.filter(account=account, alert_type=alert_type)
    context = {
        'alerts': alerts,
        'account': account
    }
    return render(request, 'facebook/account_alerts.html', context)