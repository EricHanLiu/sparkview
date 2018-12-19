import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_ovu


def main():

    accounts = DependentAccount.objects.filter(blacklisted=False)

    for account in accounts:
        if account.dependent_account_name != 'oxford properties':
            continue
        else:
            print('found oxford')
        try:
            adwords_cron_ovu(account.dependent_account_id)
        except:
            print('failed')



if __name__ == '__main__':
    main()
