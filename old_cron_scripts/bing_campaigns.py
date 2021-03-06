import os
import sys
sys.path.append('..')
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from tasks.bing_tasks import bing_cron_campaign_stats
from tasks.logger import Logger
from bloom.utils.ppc_accounts import active_bing_accounts


def main():
    accounts = active_bing_accounts()

    for acc in accounts:
        try:
            client_id = acc.bing.all()[0].id
        except:
            client_id = None
        try:
            bing_cron_campaign_stats.delay(acc.account_id, client_id)

        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for facebook_ovu.py for account ' + str(
                acc.account_name)
            warning_desc = 'Failed to create celery task for facebook_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break


if __name__ == '__main__':
    main()
