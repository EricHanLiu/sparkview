import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError

django.setup()
from facebook_dashboard.models import FacebookAccount
from tasks.facebook_tasks import facebook_cron_campaign_stats
from tasks.logger import Logger


def main():
    # accounts = FacebookAccount.objects.filter(blacklisted=False)
    accounts = FacebookAccount.objects.filter(account_name='Natrel (BLOOM)')
    for account in accounts:
        try:
            client_id = account.facebook.all()[0].id
        except:
            client_id = None

        try:
            facebook_cron_campaign_stats(account.account_id, client_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for facebook_ovu.py for account ' + str(
                account.account_name)
            warning_desc = 'Failed to create celery task for facebook_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break


if __name__ == '__main__':
    main()
