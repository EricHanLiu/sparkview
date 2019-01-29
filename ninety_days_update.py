import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client

# Simply loop through all clients and increment their phase day by 1.
# If they are at the end of their phase, start the new phase.


def main():
    accounts = Client.objects.filter(status=1)

    for account in accounts:
        account.phase_day += 1
        if account.phase_day == 31:  # Should only last 30 days, therefore on the 31st day we go to new phase
            account.phase_day = 1
            if account.phase == 3:
                account.phase = 1
            else:
                account.phase += 1
            account.save()
