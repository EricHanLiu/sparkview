from django.core.mail import send_mail
from bloom import settings


class Logger:
    """
    Logger object that can log stuff and send warnings
    """

    def __init__(self):
        self.email_addresses = settings.MAIL_ADS

    def send_warning_email(self, message, short_desc):
        if settings.DEBUG:
            message += '. DEBUG mode is on. There is a good chance this is a test.'
        send_mail(
            'SparkView Warning - ' + short_desc, message,
            settings.EMAIL_HOST_USER, self.email_addresses, fail_silently=False, html_message=message)
