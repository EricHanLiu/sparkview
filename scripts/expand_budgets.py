import os
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Budget, Client


def main():
    account_id = input('Enter account id: ')
    try:
        account = Client.objects.get(id=account_id)
    except Budget.DoesNotExist:
        print('Error, cannot find this account')
        return

    budgets = account.budgets

    for budget in budgets:
        budget.pk = None

        # Make one for just adwords
        budget.has_adwords = True
        budget.has_facebook = False
        budget.has_bing = False
        budget.save()

        budget.pk = None

        # Make one for just facebook
        budget.has_adwords = False
        budget.has_facebook = True
        budget.has_bing = False
        budget.save()

        # budget.pk = None
        #
        # # Make one for just bing
        # budget.has_adwords = False
        # budget.has_facebook = False
        # budget.has_bing = True
        # budget.save()


main()
