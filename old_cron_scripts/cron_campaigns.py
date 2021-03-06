import os
import django
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from adwords_dashboard.models import DependentAccount
from budget.models import Client
from tasks.adwords_tasks import adwords_cron_campaign_stats
from tasks.logger import Logger
from bloom.utils.ppc_accounts import active_adwords_accounts
from bloom import settings


def main():
    accounts = active_adwords_accounts()
    for account in accounts:
        try:
            client_id = account.adwords.all()[0].id
        except:
            client_id = None

        try:
            if settings.DEBUG:
                adwords_cron_campaign_stats(account.dependent_account_id, client_id)
            else:
                adwords_cron_campaign_stats.delay(account.dependent_account_id, client_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for cron_campaigns.py for account ' + str(
                account.dependent_account_name)
            warning_desc = 'Failed to create celery task for cron_campaigns.py'
            logger.send_warning_email(warning_message, warning_desc)
            break


if __name__ == '__main__':
    main()
