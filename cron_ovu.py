import os
import sys
import io
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from django.conf import settings
import gc
import logging
from datetime import datetime
import calendar
from adwords_dashboard import models
from adwords_dashboard.cron_scripts import ovu

from bloom.utils import AdwordsReportingService

def main():
    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)

    accounts = models.DependentAccount.objects.filter(blacklisted=False)
    helper = AdwordsReportingService(adwords_client)
    for account in accounts:

        last_7 = helper.get_account_performance(
            customer_id=account.dependent_account_id,
            dateRangeType="LAST_7_DAYS",
            extra_fields=["Date"]
        )

        data_this_month = helper.get_account_performance(
            customer_id=account.dependent_account_id,
            dateRangeType="THIS_MONTH",
        )


        last_7_ordered = helper.sort_by_date(last_7)
        last_7_days_cost = helper.mcv(sum([int(item['cost']) for item in last_7]))

        try:
            day_spend = last_7_days_cost / 7
        except ZeroDivisionError:
            day_spend = 0

        yesterday = last_7_ordered[-1]
        current_spend = helper.mcv(int(data_this_month[0]['cost']))
        estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
        yesterday_spend = helper.mcv(int(yesterday['cost']))

        account.estimated_spend = estimated_spend
        account.yesterday_spend = yesterday_spend
        account.current_spend = current_spend
        account.save()


if __name__ == '__main__':
    main()
