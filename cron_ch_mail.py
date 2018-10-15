import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from adwords_dashboard.models import DependentAccount
from django.core.mail import send_mail
from django.template.loader import render_to_string
from bloom.settings import TEMPLATE_DIR, EMAIL_HOST_USER


def main():
    accs = []

    MAIL_ADS = [
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
    ]

    accounts = DependentAccount.objects.filter(ch_flag=True, blacklisted=False)

    for account in accounts:
        if account.ch_flag:
            accs.append(account)

        if account.assigned_am:
            MAIL_ADS.append(account.assigned_am.email)
            print('Found AM - ' + account.assigned_am.username)
        if account.assigned_to:
            MAIL_ADS.append(account.assigned_to.email)
            print('Found CM - ' + account.assigned_to.username)
        if account.assigned_cm2:
            MAIL_ADS.append(account.assigned_cm2.email)
            print('Found CM2 - ' + account.assigned_cm2.username)
        if account.assigned_cm3:
            MAIL_ADS.append(account.assigned_cm3.email)
            print('Found CM3 - ' + account.assigned_cm3.username)

    mail_details = {
        'accounts': accs,
    }

    mail_list = set(MAIL_ADS)
    msg_html = render_to_string(TEMPLATE_DIR + '/mails/change_history_5.html', mail_details)

    send_mail(
        'No changes for more than 5 days', msg_html,
        EMAIL_HOST_USER, ['octavian@hdigital.io'], fail_silently=False, html_message=msg_html)
    mail_list.clear()

if __name__ == '__main__':
    main()