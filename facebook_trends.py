import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from facebook_dashboard.models import FacebookAccount
from tasks.facebook_tasks import facebook_result_trends

def main():
    accounts = FacebookAccount.objects.filter(blacklisted=False)
    for account in accounts:
        facebook_result_trends.delay(account.account_id)


if __name__ == '__main__':
    main()
