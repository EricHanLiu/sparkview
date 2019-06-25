from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from facebook_dashboard.models import FacebookAccount


@login_required
def account_alerts(request, account_id):
    alert_type = 'DISAPPROVED_AD'

    account = FacebookAccount.objects.get(account_id=account_id)
    context = {
        'account': account
    }
    return render(request, 'facebook/account_alerts.html', context)
