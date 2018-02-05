import os
import io
import csv
import logging
import calendar
import datetime
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from django.core.mail import send_mail
from bloom import settings
from googleads import adwords

from adwords_dashboard.models import DependentAccount

logging.basicConfig(level=logging.INFO)

start_time = time.time()
account_details = {}


def get_daily_cost(account_id, client):

    client.SetClientCustomerId(account_id)

    daily_cost = {
        'reportName': 'DAILY COST',
        'dateRangeType': 'TODAY',
        'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['Cost']
        }
    }

    service = client.GetReportDownloader(version='v201710')

    account_data = service.DownloadReportAsString(daily_cost, use_raw_enum_values=True,
                                                  skip_report_header=True, skip_report_summary=True)

    data = io.StringIO(account_data)
    data = list(csv.DictReader(data))

    account_details['account_id'] = account_id
    if data:
        account_details['daily_cost'] = float(data[0]['Cost'])/1000000

    return account_details


def setup_alert(data):

    alert = False

    now = datetime.datetime.now()
    tdays = calendar.monthrange(now.year, now.month)[1]

    aw_acc = DependentAccount.objects.get(dependent_account_id=data['account_id'])
    aw_budget = aw_acc.desired_spend

    daily_budget = aw_budget/tdays

    daily_spend = data['daily_cost']

    if daily_spend > daily_budget:
        if daily_budget > 0:
            alert = True

    if alert:
        send_mail(
            'AdWords budget pacing to fast',
            'Budget for ' + aw_acc.dependent_account_name + ' is pacing to fast. \n'
            'Daily budget: ' + str('{0:.2f}'.format(daily_budget)) + '\n'
            'Daily spend: ' + str('{0:.2f}'.format(daily_spend)),
            settings.EMAIL_HOST_USER, ['octavian.cristea@hotmail.com'], fail_silently=False
        )
        print('Mail sent!')

    return alert


def main(client, account_id):

    data = get_daily_cost(account_id, client)
    setup_alert(data)

    return data


if __name__ == '__main__':

    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    main(adwords_client, '6963071970')
    print("--- %s seconds ---" % (time.time() - start_time))