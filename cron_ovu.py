import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_ovu


def main():

    accounts = DependentAccount.objects.filter(blacklisted=False)

    for account in accounts:
        try:
            adwords_cron_ovu(account.dependent_account_id)
        except:
            print('skip')



if __name__ == '__main__':
    main()
