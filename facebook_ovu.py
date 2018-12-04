import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from facebook_dashboard.models import FacebookAccount
from tasks.facebook_tasks import facebook_cron_ovu


def main():

    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:
        try:
            facebook_cron_ovu(account.account_id)
        except:
            print('skip')


if __name__ == '__main__':
    main()
