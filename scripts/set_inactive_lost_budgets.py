import os
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from django.db.models import Q
from budget.models import Client


def main():
    """
    Sets inactive and lost accounts budgets to 0, removes all assignments
    """
    accounts = Client.objects.filter(Q(status=2) | Q(status=3))

    for account in accounts:
        for aa in account.adwords.all():
            aa.desired_spend = 0
            aa.save()
        for ba in account.bing.all():
            ba.desired_spend = 0
            ba.save()
        for fa in account.facebook.all():
            fa.desired_spend = 0
            fa.save()

        account.cm1 = None
        account.cm2 = None
        account.cm3 = None
        account.am1 = None
        account.am2 = None
        account.am3 = None
        account.seo1 = None
        account.seo2 = None
        account.seo3 = None
        account.strat1 = None
        account.strat2 = None
        account.strat3 = None

        account.save()
        print('Done ' + str(account))
