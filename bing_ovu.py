import os
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from tasks.bing_tasks import bing_cron_ovu
from tasks.logger import Logger


def main():
    clients = Client.objects.filter(salesprofile__ppc_status=1)
    # flat_list = [item for sublist in l for item in sublist]
    accounts = [acc for client in clients for acc in client.bing.all()]

    for acc in accounts:
        try:
            bing_cron_ovu.delay(acc.account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for bing_ovu.py for account ' + str(
                acc.account_name)
            warning_desc = 'Failed to create celery task for bing_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break


if __name__ == '__main__':
    main()
