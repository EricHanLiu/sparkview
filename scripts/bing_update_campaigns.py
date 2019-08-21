import os
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from bing_dashboard.cron import get_spend_by_bing_campaign_this_month
from budget.models import Client


def main():
    acc_id = input('Enter account id: ')
    try:
        account = Client.objects.get(id=acc_id)
    except Client.DoesNotExist:
        print('Error, cannot find this client')
        return
    for bing_acc in account.bing.all():
        get_spend_by_bing_campaign_this_month(bing_acc.id)


main()
