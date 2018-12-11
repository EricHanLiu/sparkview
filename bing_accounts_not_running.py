import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from bing_dashboard.models import BingAccounts
from tasks.bing_tasks import bing_accounts_not_running

def main():
    accounts = BingAccounts.objects.filter(blacklisted=False)
    for account in accounts:
        bing_accounts_not_running.delay(account.account_id)

if __name__ == '__main__':
    main()
