import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_campaign_stats


def main():

    accounts = DependentAccount.objects.filter(blacklisted=False)
    for account in accounts:
        if account.dependent_account_name != 'oxford properties':
            continue
        else:
            print('found oxford')
        try:
            client_id = account.adwords.all()[0].id
        except:
            client_id = None

        try:
            adwords_cron_campaign_stats(account.dependent_account_id, client_id)
        except:
            print('failed')



if __name__ == '__main__':
    main()
