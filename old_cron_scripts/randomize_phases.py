import os
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client


# Randomizes the phases of clients
# DO NOT RUN UNLESS YOU KNOW WHAT YOU ARE DOING


def main():
    accounts = Client.objects.filter(status=1)

    for account in accounts:
        account.phase = random.randint(1, 3)
        account.phase_day = random.randint(1, 30)

        account.save()
        print('Account ' + account.client_name + ' is now on phase ' + str(account.phase) + ' and day ' + str(
            account.phase_day) + '.')


main()
