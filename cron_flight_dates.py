import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_flight_dates

def main():

    aw = DependentAccount.objects.filter(blacklisted=False)
    for a in aw:
        adwords_cron_flight_dates.delay(a.dependent_account_id)

if __name__ == '__main__':
    main()
