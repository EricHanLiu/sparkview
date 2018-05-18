import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from facebook_dashboard.models import FacebookAccount
from tasks.facebook_tasks import facebook_cron_ovu


def main():

    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:

        facebook_cron_ovu.delay(account.account_id)


if __name__ == '__main__':
    main()