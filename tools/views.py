from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from adwords_dashboard.models import Label, DependentAccount, Campaign, Adgroup, Alert
from bing_dashboard.models import BingAccounts, BingAlerts, BingCampaign
from facebook_dashboard.models import FacebookAccount
from googleads import adwords, errors
from django.conf import settings
from django.urls import reverse
import json
from django.core import serializers
from tasks import adwords_tasks, bing_tasks
from datetime import datetime

def generate_recommendations(account):

    if account.channel == 'adwords':
        scores = [
            ('trends', account.trends_score, 'Trends'),
            ('qs', account.qs_score, 'Quality Score'),
            ('ws', account.wspend_score, 'Wasted Spend'),
            ('ch', account.changed_score[0], 'Change History'),
            ('dads', account.dads_score, 'Disapproved Ads'),
            ('nr', account.nr_score, 'Account Errors'),
            ('ext', account.ext_score, 'Extensions'),
            ('nlc', account.nlc_score, 'NLC Attribution'),
            ('keywordwastage', account.kw_score, 'Keyword Wastage')
        ]
    else:
        scores = [
            ('trends', account.trends_score, 'Change History'),
            ('qs', account.qs_score, 'Quality Score'),
            ('ws', account.wspend_score, 'Wasted Spend'),
            # ('ch', account.changed_score[0], 'Change History'),
            ('dads', account.dads_score, 'Disapproved Ads'),
            ('nr', account.nr_score, 'Account Errors'),
            ('keywordwastage', account.kw_score, 'Keyword Wastage')
            # ('ext', account.ext_score, 'Extensions'),
            # ('nlc', account.nlc_score, 'NLC Attribution')
        ]

    return sorted(scores, key=lambda tup: tup[1])


def generate_table_data(adwords, bing, report):

    data = []

    if report == 'trends':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score': round(acc.trends_score, 2),
                    'url': reverse('tools:account_results', args=(acc.dependent_account_id, acc.channel))
                },
            }
            data.append(item)

        for bacc in bing:
            item = {
                'account': 'B - ' + bacc.account_name,
                'data_score': {
                    'score': round(bacc.trends_score, 2),
                    'url': reverse('tools:account_results', args=(bacc.account_id, bacc.channel)),
                },
            }
            data.append(item)

        response = {
            'table': data,
            'column': 'Trends Report Score',
            'report': report
        }

    elif report == 'qscore':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score': round(acc.qs_score, 2),
                    'url': reverse('tools:account_qs', args=(acc.dependent_account_id, acc.channel))
                },
            }
            data.append(item)

        for bacc in bing:
            item = {
                'account': 'B - ' + bacc.account_name,
                'data_score': {
                    'score': round(bacc.qs_score, 2),
                    'url': reverse('tools:account_qs', args=(bacc.account_id, bacc.channel)),
                },
            }
            data.append(item)

        response = {
            'table': data,
            'column': 'Quality Score Report Score',
            'report': report
        }

    elif report == 'disapprovedads':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score': round(acc.dads_score, 2),
                    'url': reverse('tools:disapproved_ads', args=(acc.dependent_account_id, acc.channel)),
                },
            }
            data.append(item)

        for bacc in bing:
            item = {
                'account': 'B - ' + bacc.account_name,
                'data_score': {
                    'score': round(bacc.dads_score, 2),
                    'url': reverse('tools:disapproved_ads', args=(bacc.account_id, bacc.channel)),
                }
            }
            data.append(item)

        response = {
            'table': data,
            'column': 'Disapproved Ads Report Score',
            'report': report
        }

    elif report == 'changehistory':

        for acc in adwords:
            today = datetime.today()
            lc_val = acc.changed_data['lastChangeTimestamp']

            if lc_val != 'TOO_MANY_CHANGES' and lc_val != 'NO_ACTIVE_CAMPAIGNS':
                last_change_val = lc_val.strip(' ')[0:8]
                last_change = datetime.strptime(last_change_val, "%Y%m%d").date()
                lc_diff = today.day - last_change.day
            elif lc_val == 'TOO_MANY_CHANGES':
                lc_diff = '--'
            elif lc_val == 'NO_ACTIVE_CAMPAIGNS':
                lc_diff = '-'

            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score' :round(acc.changed_score[0], 2),
                    'url': reverse('tools:change_history', args=(acc.dependent_account_id, acc.channel))
                },
                'last_change': lc_diff
            }
            data.append(item)

        # for bacc in bing:
        #     item = ['B - ' + bacc.account_name, bacc.qs_score]
        #     data.append(item)

        response = {
            'table': data,
            'column': 'Change History Report Score',
            'column2': 'Days since last change',
            'report': report
        }

    elif report == 'notrunning':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                   'score': round(acc.nr_score, 2),
                    'url': reverse('tools:not_running', args=(acc.dependent_account_id, acc.channel))
                },
            }
            data.append(item)

        for bacc in bing:
            item = {
                'account': 'B - ' + bacc.account_name,
                'data_score': {
                    'score': round(bacc.nr_score, 2),
                    'url': reverse('tools:not_running', args=(bacc.account_id, bacc.channel)),
                }
            }
            data.append(item)

        response = {
            'table': data,
            'column': 'Account Errors Report Score',
            'report': report
        }

    elif report == 'extensions':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score': round(acc.ext_score, 2),
                    'url': reverse('tools:extensions', args=(acc.dependent_account_id, acc.channel)),
                }
            }
            data.append(item)

        # for bacc in bing:
        #     item = ['B - ' + bacc.account_name, bacc.nr_score]
        #     data.append(item)

        response = {
            'table': data,
            'column': 'Extensions Report Score',
            'report': report
        }

    elif report == 'nlc':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score': round(acc.nlc_score, 2),
                    'url': reverse('tools:nlc_attr', args=(acc.dependent_account_id, acc.channel)),
                }
            }
            data.append(item)

        # for bacc in bing:
        #     item = ['B - ' + bacc.account_name, bacc.nr_score]
        #     data.append(item)

        response = {
            'table': data,
            'column': 'NLC Attribution Model Report Score',
            'report': report
        }

    elif report == 'wspend':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score': round(acc.wspend_score, 2),
                    'url': reverse('tools:wspend', args=(acc.dependent_account_id, acc.channel)),
                }
            }
            data.append(item)

        for bacc in bing:
            item = {
                'account': 'B - ' + bacc.account_name,
                'data_score': {
                    'score': round(bacc.wspend_score, 2),
                    'url': reverse('tools:wspend', args=(bacc.account_id, bacc.channel)),
                }
            }
            data.append(item)

        response = {
            'table': data,
            'column': 'Wasted Spend Report Score',
            'report': report
        }

    elif report == 'keywordwastage':

        for acc in adwords:
            item = {
                'account': 'A - ' + acc.dependent_account_name,
                'data_score': {
                    'score': round(acc.kw_score, 2),
                    'url': reverse('tools:keyword_wastage', args=(acc.dependent_account_id, acc.channel)),
                }
            }
            data.append(item)

        for bacc in bing:
            item = {
                'account': 'B - ' + bacc.account_name,
                'data_score': {
                    'score': round(bacc.kw_score, 2),
                    'url': reverse('tools:keyword_wastage', args=(bacc.account_id, bacc.channel)),
                }
            }
            data.append(item)

        response = {
            'table': data,
            'column': 'Keyword wastage Report Score',
            'report': report
        }

    return response

# Create your views here.
@login_required
def index_tools(request):

    labels = Label.objects.filter(label_type='ACCOUNT')
    accounts = DependentAccount.objects.filter(blacklisted=False)

    context = {
        'labels': labels,
        'accounts': accounts
    }

    return render(request, 'tools/labels.html', context)

@login_required
def analyser(request):

    accounts = DependentAccount.objects.filter(blacklisted=False)
    bing_accounts = BingAccounts.objects.filter(blacklisted=False)
    facebook_accounts = FacebookAccount.objects.filter(blacklisted=False)

    context = {
        'accounts': accounts,
        'bing_accounts': bing_accounts,
        'facebook_accounts': facebook_accounts
    }
    return render(request, 'tools/ppcanalyser/analyser.html', context)

@login_required
def admin_reports(request):

    adwords = DependentAccount.objects.filter(blacklisted=False)
    bing = BingAccounts.objects.filter(blacklisted=False)
    context = {
        'adwords': adwords,
        'bing': bing
    }

    return render(request, 'tools/ppcanalyser/reports.html', context)

@login_required
def account_results(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
    elif channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)

    context = {
        'account': account,
        'trends': account.trends
    }
    return render(request, 'tools/ppcanalyser/trends.html', context)

@login_required
def account_results_weekly(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
    elif channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)

    context = {
        'account': account,
        'trends': account.trends,
        'weekly': account.weekly_data
    }
    return render(request, 'tools/ppcanalyser/trends_weekly.html', context)

@login_required
def account_overview(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
        recommendations = generate_recommendations(account)
    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
        recommendations = generate_recommendations(account)
    elif channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)

    context = {
        'account': account,
        'recommendations': recommendations[0:5]
    }

    return render(request, 'tools/ppcanalyser/overview.html', context)

@login_required
def account_qs(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
    elif channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)

    context = {
        'account': account,
        'qs_data': account.qscore_data,
        'hist_qs': account.hist_qs
    }
    return render(request, 'tools/ppcanalyser/quality_score.html', context)

@login_required
def disapproved_ads(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
        alerts = Alert.objects.filter(dependent_account_id=account_id)
    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
        alerts = BingAlerts.objects.filter(account=account)
    elif channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)

    context = {
        'account': account,
        'alerts': alerts
    }
    return render(request, 'tools/ppcanalyser/disapproved_ads.html', context)

@login_required
def change_history(request, account_id, channel):

    today = datetime.today()

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
        campaigns = Campaign.objects.filter(account=account)
        adgroups = Adgroup.objects.filter(account=account)

        try:
            last_change_val = account.changed_data['lastChangeTimestamp'].strip(' ')[0:8]
            last_change = datetime.strptime(last_change_val, "%Y%m%d").date()
            lc_diff = today.day - last_change.day
        except KeyError:
            last_change = 'Not found'
            lc_diff = 'Not found'
        except ValueError:
            last_change = 'Not found'
            lc_diff = 'Not found'

        context = {
            'account': account,
            'campaigns': campaigns,
            'adgroups': adgroups,
            'changes': account.changed_data,
            'last_change': last_change,
            'lc_diff': lc_diff
        }

    elif channel == 'bing':

        account = BingAccounts.objects.get(account_id=account_id)

        context = {
            'account': account
        }

    elif channel == 'facebook':

        account = FacebookAccount.objects.get(account_id=account_id)

    return render(request, 'tools/ppcanalyser/change_history.html', context)

@login_required
def not_running(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
    elif channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)

    context = {
        'account': account
    }

    return render(request, 'tools/ppcanalyser/not_running.html', context)

@login_required
def extensions(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)
        campaigns = Campaign.objects.filter(account=account, campaign_status='enabled', campaign_serving_status='eligible')

        context = {
            'account': account,
            'campaigns': campaigns
        }
    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
        context = {
            'account': account
        }
    elif channel == 'facebook':
        account = FacebookAccount.objects.get(account_id=account_id)
        context = {
            'account': account
        }

    return render(request, 'tools/ppcanalyser/extensions.html', context)

@login_required
def nlc_attr(request, account_id, channel):

    account = DependentAccount.objects.get(dependent_account_id=account_id)

    context = {
        'account': account
    }

    return render(request, 'tools/ppcanalyser/not_last_click.html', context)

@login_required
def wasted_spend(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)

        context = {
            'account': account
        }

    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)
        context = {
            'account': account
        }

    return render(request, 'tools/ppcanalyser/wasted_spend.html', context)


@login_required
def kw_wastage(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)

        context = {
            'account': account
        }

    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)

        context = {
            'account': account
        }

    return render(request, 'tools/ppcanalyser/kw_wastage.html', context)

@login_required
def search_queries(request, account_id, channel):

    if channel == 'adwords':
        account = DependentAccount.objects.get(dependent_account_id=account_id)

        context = {
            'account': account
        }

    elif channel == 'bing':
        account = BingAccounts.objects.get(account_id=account_id)

        context = {
            'account': account
        }

    return render(request, 'tools/ppcanalyser/search_queries.html', context)

@login_required
def get_report(request):

    report = request.GET.get('report')

    adwords = DependentAccount.objects.filter(blacklisted=False)
    bing = BingAccounts.objects.filter(blacklisted=False)

    response = generate_table_data(adwords, bing, report)

    return JsonResponse(response, safe=False)

@login_required
def run_reports(request):

    data = request.POST

    account_id = data['account_id']
    channel = data['channel']
    report = data['report']
    if channel == 'adwords':
        if report == 'results':
            adwords_tasks.adwords_result_trends.delay(account_id)
        elif report == 'qualityscore':
            adwords_tasks.adwords_account_quality_score.delay(account_id)
        elif report == 'disapprovedads':
            adwords_tasks.adwords_cron_disapproved_alert.delay(account_id)
        elif report == 'changehistory':
            adwords_tasks.adwords_account_change_history.delay(account_id)
        elif report == 'notrunning':
            adwords_tasks.adwords_account_not_running.delay(account_id)
        elif report == 'extensions':
            adwords_tasks.adwords_account_extensions.delay(account_id)
        elif report == 'nlc':
            adwords_tasks.adwords_nlc_attr_model.delay(account_id)
        elif report == 'wspend':
            adwords_tasks.adwords_account_wasted_spend.delay(account_id)
        elif report == 'keywordwastage':
            adwords_tasks.adwords_account_keyword_wastage.delay(account_id)
        elif report == 'searchqueries':
            adwords_tasks.adwords_account_search_queries.delay(account_id)
    elif channel == 'bing':
        if report == 'results':
            bing_tasks.bing_result_trends.delay(account_id)
        elif report == 'qualityscore':
            bing_tasks.bing_account_quality_score.delay(account_id)
        elif report == 'disapprovedads':
            bing_tasks.bing_cron_alerts.delay(account_id)
        elif report == 'notrunning':
            bing_tasks.bing_accounts_not_running.delay(account_id)
        elif report == 'wspend':
            bing_tasks.bing_account_wasted_spend.delay(account_id)
        elif report == 'keywordwastage':
            bing_tasks.bing_account_keyword_wastage.delay(account_id)

    elif channel == 'facebook':
        pass

    response = {}

    return JsonResponse(response)

@login_required
def create_labels(request):
    """
    creates a label that is usable for accounts

    :param labels: list with label names
    :return: the created label(s)
    :rtype: dict
    """

    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    operations = []
    labels = request.POST.get('label_name')
    labels = list(labels.split(','))
    l_type = request.POST.get('label_type')
    acc_id = request.POST.get('acc_id')

    account = DependentAccount.objects.get(account_id=acc_id)

    if not l_type:
        managed_customer_service = client.GetService('AccountLabelService', version=settings.API_VERSION)
        for label in labels:
            operations.append(
                {
                    'operator': 'ADD',
                    'operand': {
                        'name': label
                    }
                }
            )

    elif l_type == 'textlabel':

        labels_cmp = request.POST.get('label_name_cmp')
        labels_cmp = list(labels_cmp.split(','))

        client.SetClientCustomerId(acc_id)
        managed_customer_service = client.GetService('LabelService', version=settings.API_VERSION)

        for label in labels_cmp:
            operations.append(
                {
                    'operator': 'ADD',
                    'operand': {
                        'xsi_type': 'TextLabel',
                        'name': label
                    }
                }
            )

    response = {}
    c_labels = []

    for op in operations:
        try:

            result = managed_customer_service.mutate(op)
            if 'labels' in result:
                aw_response = result['labels']
                for item in aw_response:
                    c_labels.append(item['name'])
                    Label.objects.create(name=item['name'], label_id=item['id'], label_type='ACCOUNT')
                response['labels'] = c_labels

            elif 'value' in result:
                aw_response = result['value']
                for item in aw_response:
                    c_labels.append(item['name'])
                    Label.objects.create(account=account, name=item['name'], label_id=item['id'], label_type=item['Label.Type'])
                response['labels'] = c_labels

        except errors.GoogleAdsServerFault as e:
            response['error'] = e.errors[0]['reason']


    return JsonResponse(response)


@login_required
def deassign_labels(request):
    """
    removes a label from a customer account
    {'operand': {'id': 'label_id', 'xsi_type': 'Label'}, 'operator': 'REMOVE'}
    :param account_id: id of customer account
    :param label_id: id of label
    :return: managed customer label
    :rtype: dict
    """

    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    label_id = request.POST.get('label_id')
    acc_id = request.POST.get('account_id')
    account = DependentAccount.objects.get(dependent_account_id=acc_id)

    response = {}

    if 'campaign_id' in request.POST:

        client.SetClientCustomerId(acc_id)
        campaign_id = request.POST.get('campaign_id')
        campaign = Campaign.objects.get(campaign_id=campaign_id)
        campaign_service = client.GetService('CampaignService', version=settings.API_VERSION)

        operations = [
            {
                'operator': 'REMOVE',
                'operand': {
                    'xsi_type': "CampaignLabel",
                    'labelId': label_id,
                    'campaignId': campaign_id
                }
            }
        ]
        result = campaign_service.mutateLabel(operations)

        if result:
            label = Label.objects.get(label_id=label_id)
            label.campaigns.remove(campaign)
            label.save()
            response['campaign_id'] = campaign.campaign_id
            response['label_id'] = label.label_id

    elif 'adgroup_id' in request.POST:

        client.SetClientCustomerId(acc_id)
        adgroup_id = request.POST.get('adgroup_id')
        adgroup = Adgroup.objects.get(adgroup_id=adgroup_id)
        adgroup_service = client.GetService('AdGroupService', version=settings.API_VERSION)

        operations = [
            {
                'operator': 'REMOVE',
                'operand': {
                    'xsi_type': "AdGroupLabel",
                    'labelId': label_id,
                    'adGroupId': adgroup_id
                }
            }
        ]
        result = adgroup_service.mutateLabel(operations)

        if result:
            label = Label.objects.get(label_id=label_id)
            label.adgroups.remove(adgroup)
            label.save()
            response['adgroup_id'] = adgroup.adgroup_id
            response['label_id'] = label.label_id

    else:

        managed_customer_service = client.GetService('ManagedCustomerService', version=settings.API_VERSION)

        operations = [
            {
                'operator': 'REMOVE',
                'operand': {
                    'xsi_type': "ManagedCustomerLabel",
                    'labelId': label_id,
                    'customerId': acc_id
                }
            }
        ]
        result = managed_customer_service.mutateLabel(operations)

        if result:
            label = Label.objects.get(label_id=label_id)
            label.accounts.remove(account)
            label.save()

    return JsonResponse(response)


@login_required
def assign_labels(request):
    """
    adds a label to a customer account

    :param client_id: id of customer account
    :param label_id: id of label
    :return: managed customer label
    :rtype: dict
    """
    operations = []

    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    acc_id = request.POST.get('aw_acc')

    labels = request.POST.getlist('labels')
    campaigns = request.POST.getlist('campaigns')
    adgroups = request.POST.getlist('adgroups')
    account = DependentAccount.objects.get(dependent_account_id=acc_id)

    response = {}

    if 'campaigns' in request.POST and 'adgroups' in request.POST:
        for label_id in labels:
            for ag in adgroups:
                operations.append(
                    {
                        'operator': 'ADD',
                        'operand': {
                            'labelId': label_id,
                            'adGroupId': ag,
                        }
                    }
                )

        client.SetClientCustomerId(acc_id)
        adgroup_service = client.GetService('AdGroupService', version=settings.API_VERSION)
        try:
            result = adgroup_service.mutateLabel(operations)

            for item in result['value']:

                label = Label.objects.get(label_id=item['labelId'])
                adgroup = Adgroup.objects.get(adgroup_id=item['adGroupId'])
                if adgroup in label.adgroups.all():
                    continue
                else:
                    label.adgroups.add(adgroup)
        except errors.GoogleAdsServerFault as e:
            response['error'] = e.errors[0]['reason']

    elif 'campaigns' in request.POST:
        for label_id in labels:
            for cmp in campaigns:
                operations.append(
                    {
                        'operator': 'ADD',
                        'operand': {
                            'labelId': label_id,
                            'campaignId': cmp,
                        }
                    }
                )

        client.SetClientCustomerId(acc_id)
        campaign_service = client.GetService('CampaignService', version=settings.API_VERSION)
        try:
            result = campaign_service.mutateLabel(operations)

            for item in result['value']:
                label = Label.objects.get(label_id=item['labelId'])
                campaign = Campaign.objects.get(campaign_id=item['campaignId'])
                if campaign in label.campaigns.all():
                    continue
                else:
                    label.campaigns.add(campaign)

        except errors.GoogleAdsServerFault as e:
            response['error'] = e.errors[0]['reason']

    else:
        for label_id in labels:
            operations.append(
                {
                    'operator': 'ADD',
                    'operand': {
                        'xsi_type': 'ManagedCustomerLabel',
                                   'labelId': label_id,
                                   'customerId': acc_id,
                    }
                }
            )

        managed_customer_service = client.GetService('ManagedCustomerService', version=settings.API_VERSION)
        try:
            result = managed_customer_service.mutateLabel(operations)

            for item in result['value']:
                label = Label.objects.get(label_id=item['labelId'])
                if account in label.accounts.all():
                    continue
                else:
                    label.accounts.add(account)
                label.save()
        except errors.GoogleAdsServerFault as e:
            response['error'] = e.errors[0]['reason']

    response['labels'] = labels
    response['acc_name'] = account.account_name,
    response['acc_id'] = account.account_id

    return JsonResponse(response)


def get_campaigns(request):

    account_id = request.GET.get('account_id')
    campaign_id = request.GET.get('campaign_id')

    account = DependentAccount.objects.get(dependent_account_id=account_id)
    # campaign = Campaign.objects.get(campaign_id=campaign_id)


    campaigns = Campaign.objects.filter(account=account)
    campaigns_json = json.loads(serializers.serialize("json", campaigns))


    text_labels = Label.objects.filter(account=account, label_type='TextLabel')
    text_labels_json = json.loads(serializers.serialize("json", text_labels))

    response = {
        'campaigns': campaigns_json,
        'text_labels': text_labels_json
    }
    return JsonResponse(response)

def get_adgroups(request):

    account_id = request.GET.get('account_id')
    campaign_id = request.GET.get('campaign_id')

    account = DependentAccount.objects.get(dependent_account_id=account_id)
    campaign = Campaign.objects.get(campaign_id=campaign_id)

    adgroups = Adgroup.objects.filter(account=account, campaign=campaign)
    adgroups_json = json.loads(serializers.serialize("json", adgroups))

    response = {
        'adgroups': adgroups_json,

    }

    return JsonResponse(response)

def get_labels(request):

    account_id = request.GET.get('account_id')
    campaign_id = request.GET.get('campaign_id')

    account = DependentAccount.objects.get(dependent_account_id=account_id)
    campaign = Campaign.objects.get(campaign_id=campaign_id)

    if 'adgroup_id' in request.GET:
        adgroup = Adgroup.objects.get(adgroup_id=request.GET['adgroup_id'])
        labels = Label.objects.filter(account=account, adgroups=adgroup)
    else:
        labels = Label.objects.filter(account=account, campaigns=campaign)

    labels_json = json.loads(serializers.serialize("json", labels))

    response = {
        'labels': labels_json,
    }

    return JsonResponse(response)