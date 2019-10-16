# This script gets pairs of AM1s and CM1s and lists the accounts they are on together
# Writte by Sam Creamer
# October 2019
import os
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client


def main():
    accounts = Client.objects.filter(status=1)

    am_cm_pairs = {}

    for account in accounts:
        if account.am1 is None or account.cm1 is None:
            continue

        cm = account.cm1
        am = account.am1

        key = str(cm) + ', ' + str(am)

        if key not in am_cm_pairs:
            am_cm_pairs[key] = []

        am_cm_pairs[key].append(str(account))

    print('There are ' + str(len(am_cm_pairs)) + ' AM1/CM1 pairs')

    for key in am_cm_pairs:
        print(key)
        print(str(len(am_cm_pairs[key])) + ' accounts together')
        print(am_cm_pairs[key])
        print()


main()
