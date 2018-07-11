from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from adwords_dashboard.models import Label, DependentAccount, Campaign, Adgroup
from googleads import adwords
from django.conf import settings
import suds
import json
from django.core import serializers

# Create your views here.
@login_required
def index_tools(request):

    labels = Label.objects.filter(label_type='ACCOUNT')
    accounts = DependentAccount.objects.filter(blacklisted=False)

    context = {
        'labels': labels,
        'accounts': accounts
    }

    return render(request, 'tools/index.html', context)


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

    account = DependentAccount.objects.get(dependent_account_id=acc_id)

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
        except suds.WebFault as e:
            response['error'] = e.fault['detail']['ApiExceptionFault']['errors'][0]['reason'] + ': ' + op['operand']['name']


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
        result = adgroup_service.mutateLabel(operations)

        for item in result['value']:

            label = Label.objects.get(label_id=item['labelId'])
            adgroup = Adgroup.objects.get(adgroup_id=item['adGroupId'])
            if adgroup in label.adgroups.all():
                continue
            else:
                label.adgroups.add(adgroup)

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
        result = campaign_service.mutateLabel(operations)

        for item in result['value']:
            label = Label.objects.get(label_id=item['labelId'])
            campaign = Campaign.objects.get(campaign_id=item['campaignId'])
            if campaign in label.campaigns.all():
                continue
            else:
                label.campaigns.add(campaign)

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
        result = managed_customer_service.mutateLabel(operations)

        for item in result['value']:
            label = Label.objects.get(label_id=item['labelId'])
            if account in label.accounts.all():
                continue
            else:
                label.accounts.add(account)
            label.save()

    response = {
        'labels': labels,
        'acc_name': account.dependent_account_name,
        'acc_id': account.dependent_account_id
    }

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