from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from budget.models import Client
from .reports import get_ecom_ppc_best_ad_groups_query, get_organic_searches_by_region_query, \
    get_ecom_best_demographics_query, get_organic_searches_over_time_by_medium_query, get_report, \
    initialize_analyticsreporting
import json


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


@login_required
def get_ecom_best_demographics_insight(request, view_id):
    report_def = get_ecom_best_demographics_query(view_id)
    report = get_report(initialize_analyticsreporting(), report_def)

    # print(json.dumps(report, indent=4))

    data = {

    }

    return JsonResponse(data)


@login_required
def get_organic_searches_by_region_insight(request, view_id):
    report_def = get_organic_searches_by_region_query(view_id)
    report = get_report(initialize_analyticsreporting(), report_def)

    # print(json.dumps(report, indent=4))

    data = {

    }

    return JsonResponse(data)


@login_required
def get_organic_searches_over_time_by_medium_insight(request, view_id):
    report_def = get_organic_searches_over_time_by_medium_query(view_id)
    report = get_report(initialize_analyticsreporting(), report_def)

    print(json.dumps(report, indent=4))
    data = report['reports'][0]['data']
    rows = data['rows']
    bing_searches = [row['metrics'][0]['values'][0] for i, row in enumerate(rows) if i % 2 == 0]  # bing in even rows
    google_searches = [row['metrics'][0]['values'][0] for i, row in enumerate(rows) if i % 2 == 1]  # google in odd rows
    print(bing_searches, google_searches)

    data = {
        'bing_searches': bing_searches,
        'google_searches': google_searches
    }

    return JsonResponse(data)


@login_required
def get_ecom_ppc_best_ad_groups_insight(request, view_id):
    report_def = get_ecom_ppc_best_ad_groups_query(view_id)
    report = get_report(initialize_analyticsreporting(), report_def)

    # print(json.dumps(report, indent=4))

    data = {

    }

    return JsonResponse(data)
