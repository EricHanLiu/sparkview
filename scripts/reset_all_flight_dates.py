import os
import sys
import django

sys.path.append('..')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()

from budget.cron import reset_all_flight_date_spend_objects


def main():
    reset_all_flight_date_spend_objects()


main()
