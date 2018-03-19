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

# 99% - budget protection script

def build_data():

    now = datetime.datetime.now()
    days = calendar.monthrange(now.year, now.month)[1]
    remaining = days - now.day

    users = User.objects.all()

    for user in users:

        aw_accounts = user.profile.adwords.all()

        for a in aw_accounts:
            spend = a.current_spend
            daily_spend = spend / now.day
            projected = (daily_spend * remaining) + spend
            try:
                percentage = (projected * 100) / a.desired_spend
            except ZeroDivisionError:
                continue

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
            daily_spend = spend / now.day
            projected = (daily_spend * remaining) + spend
            try:
                percentage = (projected * 100) / b.desired_spend
            except ZeroDivisionError:
                continue

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

        msg_plain = render_to_string(settings.TEMPLATE_DIR + '/mails/budget_breakfast.txt', mail_details)
        msg_html = render_to_string(settings.TEMPLATE_DIR + '/mails/budget_breakfast.html', mail_details)

        send_mail(
            'Daily budget report', msg_plain,
            settings.EMAIL_HOST_USER, [user.email], fail_silently=False, html_message=msg_html
        )
        print('Mail sent!')

        del aw_overspenders[:]
        del aw_underspenders[:]
        del bing_over[:]
        del bing_under[:]

def main():

    build_data()


if __name__ == '__main__':

    main()
    print('\n')
    print("--- %s seconds ---" % (time.time() - start_time))