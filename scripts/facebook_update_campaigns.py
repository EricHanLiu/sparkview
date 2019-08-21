import os
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from facebook_dashboard.cron import get_spend_by_facebook_campaign_this_month
from budget.models import Client


def main():
    acc_id = input('Enter account id: ')
    try:
        account = Client.objects.get(id=acc_id)
    except Client.DoesNotExist:
        print('Error, cannot find this client')
        return
    print('Updating facebook accounts for ' + str(account))
    for fb_acc in account.facebook.all():
        get_spend_by_facebook_campaign_this_month(fb_acc.id)


main()