import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from django.shortcuts import get_object_or_404
from budget.models import Client
from django.contrib.auth.models import User
from client_area.models import AccountHourRecord
from user_management.models import Member


"""
This script should restore hours lost from November 2018 data loss
"""

print('Restoring hours')

mast = open("hoursRestoreNov2018", "r")

# id, hours, month, year, account_id, member_id,
for line in mast:
    s = line.split('\t')

    hours = s[1]
    month = s[2]
    year = s[3]
    account_id = s[4]
    try:
        account = Client.objects.get(id=account_id)
    except:
        continue
    member_id = s[5]
    try:
        member = Member.objects.get(id=member_id)
    except:
        member = Member.objects.get(id=1)

    AccountHourRecord.objects.create(hours=hours, month=month, year=year, account=account, member=member)

    print('Created an hour record with ' + str(hours) + ' hours for account ' + account.client_name + ' for ' + member.user.get_full_name() + '.')
