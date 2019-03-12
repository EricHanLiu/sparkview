import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client
import datetime
# Simply loop through all clients and increment their phase day by 1.
# If they are at the end of their phase, start the new phase.


def main():
    accounts = Client.objects.filter(status=1)

    for account in accounts:
        print(account.client_name + ' day was ' + str(account.phase_day))
        account.phase_day += 1
        if account.phase_day == 31:  # Should only last 30 days, therefore on the 31st day we go to new phase
            account.phase_day = 1
            if account.phase == 3:
                account.phase = 1
            else:
                account.phase += 1
        print(account.client_name + ' day is now ' + str(account.phase_day))
        account.save()
    print('done on ' + str(datetime.datetime.now()))


# main()
