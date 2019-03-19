import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()

from client_area.models import UpsellAttempt, LifecycleEvent
from budget.models import Client
from user_management.models import Member

file = open('upsell.csv', 'r')
reader = csv.reader(file, delimiter=',')

counter = 0

try:
    phil = Member.objects.get(id=46)
except Member.DoesNotExist:
    phil = None

for row in reader:
    counter += 1
    if counter <= 2:  # Skips the first line (headers)
        continue

    name = row[0]

    try:
        account = Client.objects.get(client_name__contains=name)
    except (Client.DoesNotExist, Client.MultipleObjectsReturned) as e:
        print(e)
        continue

    # Go through each type of upsell

    # PPC
    if row[2] == 'TRUE':
        ua = UpsellAttempt()
        ua.account = account
        ua.service = 1
        ua.result = 3
        ua.attempted_by = phil
        ua.save()
        lc_event = LifecycleEvent.objects.create(account=account, type=1, description=str(ua),
                                                 related_upsell=ua,
                                                 phase=account.phase,
                                                 phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                 bing_active=account.has_bing,
                                                 facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                 monthly_budget=account.current_budget, spend=account.current_spend)

    # SEO
    if row[4] == 'TRUE':
        ua = UpsellAttempt()
        ua.account = account
        ua.service = 2
        ua.result = 3
        ua.attempted_by = phil
        ua.save()
        lc_event = LifecycleEvent.objects.create(account=account, type=1, description=str(ua),
                                                 related_upsell=ua,
                                                 phase=account.phase,
                                                 phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                 bing_active=account.has_bing,
                                                 facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                 monthly_budget=account.current_budget, spend=account.current_spend)

    # CRO
    if row[6] == 'TRUE':
        ua = UpsellAttempt()
        ua.account = account
        ua.service = 3
        ua.result = 3
        ua.attempted_by = phil
        ua.save()
        lc_event = LifecycleEvent.objects.create(account=account, type=1, description=str(ua),
                                                 related_upsell=ua,
                                                 phase=account.phase,
                                                 phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                 bing_active=account.has_bing,
                                                 facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                 monthly_budget=account.current_budget, spend=account.current_spend)

    # Strat
    if row[8] == 'TRUE':
        ua = UpsellAttempt()
        ua.account = account
        ua.service = 4
        ua.result = 3
        ua.attempted_by = phil
        ua.save()
        lc_event = LifecycleEvent.objects.create(account=account, type=1, description=str(ua),
                                                 related_upsell=ua,
                                                 phase=account.phase,
                                                 phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                 bing_active=account.has_bing,
                                                 facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                 monthly_budget=account.current_budget, spend=account.current_spend)

    # Feed Management
    if row[10] == 'TRUE':
        ua = UpsellAttempt()
        ua.account = account
        ua.service = 5
        ua.result = 3
        ua.attempted_by = phil
        ua.save()
        lc_event = LifecycleEvent.objects.create(account=account, type=1, description=str(ua),
                                                 related_upsell=ua,
                                                 phase=account.phase,
                                                 phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                 bing_active=account.has_bing,
                                                 facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                 monthly_budget=account.current_budget, spend=account.current_spend)

    # Email marketing
    if row[12] == 'TRUE':
        ua = UpsellAttempt()
        ua.account = account
        ua.service = 6
        ua.result = 3
        ua.attempted_by = phil
        ua.save()
        lc_event = LifecycleEvent.objects.create(account=account, type=1, description=str(ua),
                                                 related_upsell=ua,
                                                 phase=account.phase,
                                                 phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                 bing_active=account.has_bing,
                                                 facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                 monthly_budget=account.current_budget, spend=account.current_spend)
