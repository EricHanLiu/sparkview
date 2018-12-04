import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from budget.models import Client, TierChangeProposal

accounts = Client.objects.filter(status=1)

for account in accounts:
    if account.tier != account.calculated_tier:
        proposal, created = TierChangeProposal.objects.get_or_create(account=account, tier_from=account.tier, tier_to=account.calculated_tier)
        if created:
            print('Created proposal for ' + account.client_name)
