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
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from bloom import settings
from googleads import adwords

from adwords_dashboard.models import DependentAccount
from bing_dashboard.models import BingAccounts

logging.basicConfig(level=logging.INFO)

start_time = time.time()
aw_underspenders = []
aw_overspenders = []
bing_under = []
bing_over = []
aw_campaigns = []

now = datetime.datetime.today()
current_day = now.day - 1
days = calendar.monthrange(now.year, now.month)[1]
remaining = days - current_day

# 99% - budget protection script


def get_campaigns(client):


    offset = 0
    PAGE_SIZE = 500

    client.SetClientCustomerId('7637584053')

    campaign_service = client.GetService('CampaignService', version=settings.API_VERSION)

    campaign_selector = {'fields': ['Id', 'Status','Name'],
                         'predicates': [
                             {
                                 'field': 'Status',
                                 'operator': 'EQUALS',
                                 'values': 'ENABLED'
                             }],
                         'paging': {
                             'startIndex': str(offset),
                             'numberResults': str(PAGE_SIZE)
                         }}
    more_pages = True

    while more_pages:

        page = campaign_service.get(campaign_selector)
        time.sleep(0.5)

        if 'entries' in page and page['entries']:

            aw_campaigns.extend(page['entries'])
            offset += PAGE_SIZE
            campaign_selector['paging']['startIndex'] = str(offset)

        more_pages = offset < int(page['totalNumEntries'])

    return aw_campaigns

def budget_breakfast():

    users = User.objects.all()

    for user in users:

        aw_accounts = user.profile.adwords.all()

        for a in aw_accounts:
            spend = a.current_spend
            daily_spend = spend / current_day
            projected = (daily_spend * remaining) + spend
            try:
                percentage = (projected * 100) / a.desired_spend
            except ZeroDivisionError:
                continue
            print('Percentage [AW]: ' + str(percentage))
            if percentage < 90:

                details = {
                    'account': a.dependent_account_name,
                    'estimated': percentage,
                    'budget': a.desired_spend,
                    'current_spend': a.current_spend,
                    'projected': round(projected, 2)
                }
                aw_underspenders.append(details)

            elif percentage > 99:

                details = {
                    'account': a.dependent_account_name,
                    'estimated': percentage,
                    'budget': a.desired_spend,
                    'current_spend': a.current_spend,
                    'projected': projected
                }
                aw_overspenders.append(details)

        bing_accounts = user.profile.bing.all()

        for b in bing_accounts:
            spend = b.current_spend
            daily_spend = spend / current_day
            projected = (daily_spend * remaining) + spend
            try:
                percentage = (projected * 100) / b.desired_spend
            except ZeroDivisionError:
                continue

            print('Percentage [B]: ' + str(percentage))

            if percentage < 90:

                details = {
                    'account': b.account_name,
                    'estimated': percentage,
                    'budget': b.desired_spend,
                    'current_spend': b.current_spend,
                    'projected': projected
                }
                bing_under.append(details)

            elif percentage > 99:

                details = {
                    'account': b.account_name,
                    'estimated': percentage,
                    'budget': b.desired_spend,
                    'current_spend': b.current_spend,
                    'projected': projected
                }
                bing_over.append(details)

        mail_details = {
            'aw_under': aw_underspenders,
            'aw_over': aw_overspenders,
            'bing_under': bing_under,
            'bing_over': bing_over,
            'user': user.get_full_name()
        }

        print(mail_details)

        msg_plain = render_to_string(settings.TEMPLATE_DIR + '/mails/budget_breakfast.txt', mail_details)
        msg_html = render_to_string(settings.TEMPLATE_DIR + '/mails/budget_breakfast.html', mail_details)

        send_mail(
            'Daily budget report', msg_plain,
            settings.EMAIL_HOST_USER, ['octavian@hdigital.io'], fail_silently=False, html_message=msg_html
        )
        print('Mail sent!')

        del aw_overspenders[:]
        del aw_underspenders[:]
        del bing_over[:]
        del bing_under[:]


def budget_protection(client):

    percentage = 0

    users = User.objects.all()

    for user in users:

        aw_accounts = user.profile.adwords.all()
        bing_accounts = user.profile.bing.all()

        for a in aw_accounts:


            spend = a.current_spend
            daily_spend = spend / current_day
            projected = (daily_spend * remaining) + spend
            protected = a.protected

            try:
                percentage = (projected * 100) / a.desired_spend
            except ZeroDivisionError:
                continue

            if percentage >= 99:

                if protected:

                    # pausing all campaigns from the adwords account

                    client.SetClientCustomerId(a.dependent_account_id)

                    campaign_service = client.GetService('CampaignService', version=settings.API_VERSION)

                    offset = 0

                    selector = {
                        'fields': ['Id', 'Name', 'Status'],
                        'paging': {
                            'startIndex': str(offset),
                            'numberResults': str(PAGE_SIZE)
                        },
                        'predicates': [
                            {
                                'field': 'Status',
                                'operator': 'EQUALS',
                                'values': 'ENABLED'
                        }],
                    }

                    more_pages = True

                    while more_pages:

                        page = campaign_service.get(selector)

                        if 'entries' in page and page['entries']:
                            aw_campaigns.extend(page['entries'])
                            offset += self.PAGE_SIZE
                            campaign_selector['paging']['startIndex'] = str(offset)

                        more_pages = offset < int(page['totalNumEntries'])

                    # Loop thorugh campaign list and pause them
                    for cmp in aw_campaigns:

                        campaign_criterion = {
                            'campaignId': cmp['Campaign ID'],
                            'status': 'PAUSED'
                        }

                        # Create operations.
                        operations = [
                            {
                                'operator': 'SET',
                                'operand': campaign_criterion
                            }
                        ]

                        # Make the mutate request.
                        result = campaign_criterion_service.mutate(operations)


        for b in bing_accounts:

            spend = b.current_spend
            daily_spend = spend / current_day
            projected = (daily_spend * remaining) + spend
            protected = b.protected

            try:
                percentage = (projected * 100) / b.desired_spend
            except ZeroDivisionError:
                continue

            if percentage >= 99:

                if protected:

                    # pausing all campaigns from bing account
                    pass

def main():

    # client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    # print(get_campaigns(client))
    budget_breakfast()


if __name__ == '__main__':

    main()
    print('\n')
    print("--- %s seconds ---" % (time.time() - start_time))