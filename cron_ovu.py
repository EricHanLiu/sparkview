import sys
import io
import logging
import os
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom.settings import ADWORDS_YAML
from datetime import datetime
from adwords_dashboard.models import DependentAccount
from bloom.utils import AdwordsReportingService

logging.basicConfig(level=logging.INFO)

def main():
    adwords_client = adwords.AdWordsClient.LoadFromStorage(ADWORDS_YAML)

    accounts = DependentAccount.objects.filter(blacklisted=False)
    helper = AdwordsReportingService(adwords_client)
    this_month = helper.get_this_month_daterange()
    for account in accounts:

        last_7 = helper.get_account_performance(
            customer_id=account.dependent_account_id,
            dateRangeType="LAST_7_DAYS",
            extra_fields=["Date"]
        )

        data_this_month = helper.get_account_performance(
            customer_id=account.dependent_account_id,
            dateRangeType="CUSTOM_DATE",
            **this_month
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
