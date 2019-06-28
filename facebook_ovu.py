import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError

django.setup()
from tasks.facebook_tasks import facebook_cron_ovu
from tasks.logger import Logger
from bloom.utils.ppc_accounts import ppc_active_accounts_for_platform


def main():
    accounts = ppc_active_accounts_for_platform('facebook')

    for account in accounts:
        try:
            facebook_cron_ovu.delay(account.account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for facebook_ovu.py for account ' + str(
                account.account_name)
            warning_desc = 'Failed to create celery task for facebook_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break


if __name__ == '__main__':
    main()
