import os
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_ovu

logging.basicConfig(level=logging.INFO)

def main():

    accounts = DependentAccount.objects.filter(blacklisted=False)

    for account in accounts:
        adwords_cron_ovu.delay(account.dependent_account_id)



if __name__ == '__main__':
    main()
