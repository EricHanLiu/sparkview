import os
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_ovu
from tasks.logger import Logger


def main():
    accounts = DependentAccount.objects.filter(blacklisted=False)
    for account in accounts:
        try:
            adwords_cron_ovu.delay(account.dependent_account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for cron_ovu.py for account ' + str(
                account.dependent_account_name)
            warning_desc = 'Failed to create celery task for cron_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break


if __name__ == '__main__':
    main()
