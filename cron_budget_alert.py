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
from itertools import chain
from adwords_dashboard.models import DependentAccount
from bing_dashboard.models import BingAccounts
from facebook_dashboard.models import FacebookAccount
from user_management.models import Member

logging.basicConfig(level=logging.INFO)

start_time = time.time()
aw_campaigns = []

now = datetime.datetime.today()
current_day = now.day - 1
days = calendar.monthrange(now.year, now.month)[1]
remaining = days - current_day


# 99% - budget protection script

def check_spend(accounts, user):
    under = []
    over = []
    nods = []
    on_pace = []
    flex = []

    members = Member.objects.all()
    for member in members:
        if member.user == user:
            accs = member.get_accounts()
            print(accs)
            for acc in accs:
                if acc.flex_budget > 0:

                    average_projected = ((acc.current_spend / current_day) * remaining) + acc.current_spend
                    ys_projected = acc.yesterday_spend * remaining + acc.current_spend

                    details = {
                        'client': acc.client_name,
                        'budget': acc.budget,
                        'current_spend': acc.current_spend,
                        'average_projected': round(average_projected, 2),
                        'ys_projected': round(ys_projected, 2)
                    }
                    flex.append(details)

    for account in accounts:

        spend = account.current_spend
        projected = account.yesterday_spend * remaining + spend

        try:
            percentage = (projected * 100) / account.desired_spend
        except ZeroDivisionError:
            percentage = 0

        if account.desired_spend == 0:

            if account.channel == 'adwords':

                details = {
                    'account': account.dependent_account_name,
                    'budget': account.desired_spend,
                    'channel': account.channel
                }
                nods.append(details)
            else:
                details = {
                    'account': account.account_name,
                    'budget': account.desired_spend,
                    'channel': account.channel
                }
                nods.append(details)
        elif account.desired_spend <= 10000:
            if percentage < 90:
                if account.channel == 'adwords':

                    details = {
                        'account': account.dependent_account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    under.append(details)
                else:
                    details = {
                        'account': account.account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    under.append(details)
            elif percentage > 99:
                if account.channel == 'adwords':
                    details = {
                        'account': account.dependent_account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    over.append(details)
                else:
                    details = {
                        'account': account.account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    over.append(details)
            elif 90 > percentage < 99:
                if account.channel == 'adwords':
                    details = {
                        'account': account.dependent_account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    on_pace.append(details)
                else:
                    details = {
                        'account': account.account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    on_pace.append(details)
        elif account.desired_spend > 10000:
            if percentage < 95:
                if account.channel == 'adwords':

                    details = {
                        'account': account.dependent_account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    under.append(details)
                else:
                    details = {
                        'account': account.account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    under.append(details)
            elif percentage > 99:
                if account.channel == 'adwords':
                    details = {
                        'account': account.dependent_account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    over.append(details)
                else:
                    details = {
                        'account': account.account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    over.append(details)
            elif 95 > percentage < 99:
                if account.channel == 'adwords':
                    details = {
                        'account': account.dependent_account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    on_pace.append(details)
                else:
                    details = {
                        'account': account.account_name,
                        'estimated': percentage,
                        'budget': account.desired_spend,
                        'current_spend': account.current_spend,
                        'channel': account.channel,
                        'projected': round(projected, 2)
                    }
                    on_pace.append(details)

    mail_details = {
        'under': under,
        'over': over,
        'nods': nods,
        'on_pace': on_pace,
        'flex': flex,
        'user': user.get_full_name()
    }

    return mail_details


# def get_campaigns(client):
#     offset = 0
#     PAGE_SIZE = 500
#
#     client.SetClientCustomerId('7637584053')
#
#     campaign_service = client.GetService('CampaignService', version=settings.API_VERSION)
#
#     campaign_selector = {'fields': ['Id', 'Status', 'Name'],
#                          'predicates': [
#                              {
#                                  'field': 'Status',
#                                  'operator': 'EQUALS',
#                                  'values': 'ENABLED'
#                              }],
#                          'paging': {
#                              'startIndex': str(offset),
#                              'numberResults': str(PAGE_SIZE)
#                          }}
#     more_pages = True
#
#     while more_pages:
#
#         page = campaign_service.get(campaign_selector)
#         time.sleep(0.5)
#
#         if 'entries' in page and page['entries']:
#             aw_campaigns.extend(page['entries'])
#             offset += PAGE_SIZE
#             campaign_selector['paging']['startIndex'] = str(offset)
#
#         more_pages = offset < int(page['totalNumEntries'])
#
#     return aw_campaigns


def budget_breakfast():
    users = User.objects.all()

    for user in users:
        aw_accounts = DependentAccount.objects.filter(assigned_to=user)
        aw_cm2 = DependentAccount.objects.filter(assigned_cm2=user)
        aw_cm3 = DependentAccount.objects.filter(assigned_cm3=user)
        aw_am = DependentAccount.objects.filter(assigned_am=user)

        bing_accounts = BingAccounts.objects.filter(assigned_to=user)
        bing_cm2 = BingAccounts.objects.filter(assigned_cm2=user)
        bing_cm3 = BingAccounts.objects.filter(assigned_cm3=user)
        bing_am = BingAccounts.objects.filter(assigned_am=user)

        fb_accounts = FacebookAccount.objects.filter(assigned_to=user)
        fb_cm2 = FacebookAccount.objects.filter(assigned_cm2=user)
        fb_cm3 = FacebookAccount.objects.filter(assigned_cm3=user)
        fb_am = FacebookAccount.objects.filter(assigned_am=user)

        accounts = list(chain(
            aw_accounts,
            aw_cm2,
            aw_cm3,
            aw_am,
            bing_accounts,
            bing_cm2,
            bing_cm3,
            bing_am,
            fb_accounts,
            fb_cm2,
            fb_cm3,
            fb_am
        ))

        mail_details = check_spend(accounts, user)

        msg_html = render_to_string(settings.TEMPLATE_DIR + '/mails/budget_breakfast.html', mail_details)

        send_mail(
            'Daily budget report', msg_html,
            settings.EMAIL_HOST_USER, [user.email], fail_silently=False, html_message=msg_html
        )
        print('Mail sent!')


# def budget_protection(client):
#
#     users = User.objects.all()
#
#     for user in users:
#
#         aw_accounts = user.profile.adwords.all()
#
#         for a in aw_accounts:
#
#             spend = a.current_spend
#             daily_spend = spend / current_day
#             projected = (daily_spend * remaining) + spend
#             protected = a.protected
#
#             try:
#                 percentage = (projected * 100) / a.desired_spend
#             except ZeroDivisionError:
#                 continue
#
#             if percentage >= 99:
#
#                 if protected:
#
#                     # pausing all campaigns from the adwords account
#
#                     client.SetClientCustomerId(a.dependent_account_id)
#
#                     campaign_service = client.GetService('CampaignService', version=settings.API_VERSION)
#
#                     offset = 0
#
#                     selector = {
#                         'fields': ['Id', 'Name', 'Status'],
#                         'paging': {
#                             'startIndex': str(offset),
#                             'numberResults': str(PAGE_SIZE)
#                         },
#                         'predicates': [
#                             {
#                                 'field': 'Status',
#                                 'operator': 'EQUALS',
#                                 'values': 'ENABLED'
#                             }],
#                     }
#
#                     more_pages = True
#
#                     while more_pages:
#
#                         page = campaign_service.get(selector)
#
#                         if 'entries' in page and page['entries']:
#                             aw_campaigns.extend(page['entries'])
#                             offset += self.PAGE_SIZE
#                             selector['paging']['startIndex'] = str(offset)
#
#                         more_pages = offset < int(page['totalNumEntries'])
#
#                     # Loop thorugh campaign list and pause them
#                     for cmp in aw_campaigns:
#                         campaign_id = cmp['Campaign ID']
#
#                         # Create operations.
#                         operations = [{
#                             'operator': 'SET',
#                             'operand': {
#                                 'id': campaign_id,
#                                 'status': 'PAUSED'
#                             }
#                         }]
#
#                         # Pause campaign if percentage > 99
#                         result = campaign_service.mutate(operations)
#                         print(result)


def main():
    budget_breakfast()


if __name__ == '__main__':
    main()
    print('\n')
    print("--- %s seconds ---" % (time.time() - start_time))
