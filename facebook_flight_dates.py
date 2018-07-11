import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from facebook_dashboard.models import FacebookAccount
from tasks.facebook_tasks import facebook_cron_flight_dates



def main():

    fb = FacebookAccount.objects.filter(blacklisted=False)
    for f in fb:
        facebook_cron_flight_dates.delay(f.account_id)


if __name__ == '__main__':
    main()
