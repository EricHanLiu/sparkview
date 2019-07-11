from django.shortcuts import render
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from .management import initialize_analyticsmanagement, get_accounts as get_ga_accounts, \
    get_properties as get_ga_properties, get_views as get_ga_views
from .reports import get_ecom_ppc_best_ad_groups_query, get_organic_searches_by_region_query, \
    get_ecom_best_demographics_query, get_organic_searches_over_time_by_medium_query, get_report, \
    initialize_analyticsreporting, get_content_group_query
import json


@login_required
def insights(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    return render(request, 'insights/insights.html')


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

    data = report['reports'][0]['data']
    rows = data['rows']

    data = {
        'regionData': [
            {
                'region': row['dimensions'][0],
                'searches': row['metrics'][0]['values'][0],
                'avgPageLoad': row['metrics'][0]['values'][1]

            } for row in rows
        ]
    }

    data['regionData'] = data['regionData'][0:5]  # top 5 regions only

    return JsonResponse(data)


@login_required
def get_organic_searches_over_time_by_medium_insight(request, view_id):
    report_def = get_organic_searches_over_time_by_medium_query(view_id)
    report = get_report(initialize_analyticsreporting(), report_def)

    data = report['reports'][0]['data']
    rows = data['rows']
    bing_searches = [row['metrics'][0]['values'][0] for i, row in enumerate(rows) if i % 2 == 0]  # bing in even rows
    google_searches = [row['metrics'][0]['values'][0] for i, row in enumerate(rows) if i % 2 == 1]  # google in odd rows

    data = {
        'bing_searches': bing_searches,
        'google_searches': google_searches
    }

    return JsonResponse(data)


@login_required
def get_content_group_insight(request, view_id):
    report_def = get_content_group_query(view_id)
    report = get_report(initialize_analyticsreporting(), report_def)

    print(json.dumps(report, indent=4))

    data = {

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


@login_required
def get_views(request):
    """
    Gets all accounts that bloom has
    :param request:
    :return:
    """
    if not request.user.is_staff:
        return HttpResponseForbidden('Bye')

    prop_id = request.POST.get('prop_id')
    account_id = request.POST.get('account_id')

    analytics = initialize_analyticsmanagement()
    return JsonResponse(get_ga_views(analytics, account_id, prop_id))
