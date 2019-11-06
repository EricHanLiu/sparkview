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

        am_cm_pairs[key].append(
            str(account) + '\t' + str(account.tier) + '\t' + str(account.default_budget.budget) + '\t' + str(
                account.clientType) + '\t' + str(round(account.ppc_hours * 0.25, 0)) + '\t' + str(
                round(account.ppc_hours * 0.75, 0)))

    print('There are ' + str(len(am_cm_pairs)) + ' AM1/CM1 pairs')

    for key in am_cm_pairs:
        unpickle = key.split(', ')
        cm = unpickle[0]
        am = unpickle[1]
        for a in am_cm_pairs[key]:
            print(str(am) + '\t' + str(cm) + '\t' + a)


main()
