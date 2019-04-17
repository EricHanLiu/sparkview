import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_ovu
from user_management.models import Member


def main():
    accounts = DependentAccount.objects.filter(blacklisted=False)
    sam = Member.objects.get(id=1)
    sams_accounts = []
    for acc in sam.accounts:
        for a_acc in acc.adwords.all():
            sams_accounts.append(a_acc)
    for account in accounts:
        try:
            if account in sams_accounts:
                adwords_cron_ovu(account.dependent_account_id)
        except:
            print('exception')


if __name__ == '__main__':
    main()
