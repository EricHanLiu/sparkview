from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from budget.models import Client


@login_required
def insights(request, account_pk=None):
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    if account_pk is None:
        account = 'Insights'
    else:
        account = Client.objects.get(pk=account_pk)

    context = {
        'account': account
    }

    return render(request, 'insights/insights.html', context)
