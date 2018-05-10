import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_anomalies

def main():
    accounts = DependentAccount.objects.filter(blacklisted=False)
    for account in accounts:
        adwords_cron_anomalies.delay(account.dependent_account_id)



if __name__ == '__main__':
    main()
