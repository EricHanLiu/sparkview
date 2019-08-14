import os
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.cron import create_default_budgets


def main():
    create_default_budgets.delay()


main()
