from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from adwords_dashboard.models import Label, DependentAccount
from googleads import adwords
from django.conf import settings


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

    :param label_name: the name of the label
    :return: the created label
    :rtype: dict
    """

    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    operations = []
    labels = request.POST.get('label_name')
    labels = list(labels.split(','))

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

    result = managed_customer_service.mutate(operations)

    labels = []

    aw_response = dict(result['labels'])
    if aw_response:
        for key, value in aw_response.items():
            labels.append(value[1])
            Label.objects.create(name=value[1], label_id=key[1], label_type='ACCOUNT')

    response = {
        'labels': labels
    }

    return JsonResponse(response)


@login_required
def deassign_labels(request):
    """
    removes a label from a customer account

    :param account_id: id of customer account
    :param label_id: id of label
    :return: managed customer label
    :rtype: dict
    """
    label_id = request.POST.get('label_id')
    acc_id = request.POST.get('account_id')
    account = DependentAccount.objects.get(dependent_account_id=acc_id)
    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
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
    print(result)
    if result:
        label = Label.objects.get(label_id=label_id)
        label.accounts.remove(account)
        label.save()

    response = {}
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
    acc_id = request.POST.get('aw_acc')
    labels = request.POST.getlist('labels')
    account = DependentAccount.objects.get(dependent_account_id=acc_id)

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
    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    managed_customer_service = client.GetService('ManagedCustomerService', version=settings.API_VERSION)

    result = managed_customer_service.mutateLabel(operations)
    print(result)
    if result:
        for label_id in labels:
            label = Label.objects.get(label_id=label_id)
            label.accounts.add(account)
            label.save()

    response = {
    }
    return JsonResponse(response)
