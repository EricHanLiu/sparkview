import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from bing_dashboard.models import BingAccounts
from tasks.bing_tasks import bing_account_keyword_wastage

def main():
    accounts = BingAccounts.objects.filter(blacklisted=False)
    for account in accounts:
        bing_account_keyword_wastage.delay(account.account_id)


if __name__ == '__main__':
    main()
