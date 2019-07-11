from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from budget.models import Client
from .models import Opportunity


@login_required
def insights(request, account_id=None):
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    if account_id is None:
        account = None
    else:
        account = get_object_or_404(Client, id=account_id)

    context = {
        'account': account,
    }

    return render(request, 'insights/insights.html', context)
