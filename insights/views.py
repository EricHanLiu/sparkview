from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from budget.models import Client
from .management import initialize_analyticsmanagement, get_accounts as get_ga_accounts, \
    get_properties as get_ga_properties
from .models import Opportunity


@login_required
def insights(request, account_id=None):
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    if account_id is None:
        account = None
        opportunities = Opportunity.objects.all()
    else:
        account = get_object_or_404(Client, id=account_id)
        opportunities = Opportunity.objects.filter(report__account=account)

    context = {
        'account': account,
        'opportunities': opportunities
    }

    return render(request, 'insights/insights.html', context)


@login_required
def get_accounts(request):
    """
    Gets all accounts that bloom has
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    analytics = initialize_analyticsmanagement()
    return JsonResponse(get_ga_accounts(analytics))


@login_required
def get_properties(request):
    """
    Gets all accounts that bloom has
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    account_id = request.POST.get('account_id')

    analytics = initialize_analyticsmanagement()
    return JsonResponse(get_ga_properties(analytics, account_id))
