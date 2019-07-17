import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from django.core.mail import send_mail
from django.template.loader import render_to_string
from bloom.settings import TEMPLATE_DIR, EMAIL_HOST_USER
from bloom.utils.ppc_accounts import active_adwords_accounts


def main():
    mail_list = {
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
        'avi@makeitbloom.com'
    }

    accounts = [acc for acc in active_adwords_accounts() if acc.ch_flag]

    mail_details = {
        'accounts': accounts,
    }

    msg_html = render_to_string(TEMPLATE_DIR + '/mails/change_history_5.html', mail_details)

    send_mail(
        'No changes for more than 5 days', msg_html,
        EMAIL_HOST_USER, mail_list, fail_silently=False, html_message=msg_html)
    mail_list.clear()


if __name__ == '__main__':
    main()
