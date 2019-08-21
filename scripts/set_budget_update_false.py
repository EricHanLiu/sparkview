import os
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client


# Sets all budget updated flags to false at beginning of the month


def main():
    accounts = Client.objects.all()

    for account in accounts:
        account.budget_updated = False
        account.save()


main()
