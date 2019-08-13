import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
import sys
django.setup()
import datetime
from user_management.models import Member, BackupPeriod, Backup
from budget.models import Client
from client_area.models import Promo

"""
Makes emergency backup for Bloom
"""
#mcsv = open('members.csv', 'w+')
#bcsv = open('backups.csv', 'w+')

d = datetime.datetime.now()
two_weeks_ago = d - datetime.timedelta(14)

#mcsv.write('Created ' + d + '\r\n')
#bcsv.write('Created ' + d + '\r\n')

members = Member.objects.all()
accounts = Client.objects.filter(status=1)
backup_periods = BackupPeriod.objects.filter(start_date__gte=two_weeks_ago)

# Accounts
acsv = open('accounts.csv', 'w+')
acsv.write('Created ' + str(d) + '\r\n\r\n')
acsv.write('Account, Budget, SEO Hours, CRO Hours, Promos\r\n')
for account in accounts:
    promos = Promo.objects.filter(account=account, start_date__gte=two_weeks_ago)
    promo_str = ''
    for promo in promos:
        promo_str += str(promo) + ', '

    acsv.write(account.client_name + ', ' + str(account.current_budget) + ', ' + str(account.seo_hours) + ', ' + str(account.cro_hours) + ', ' + promo_str + '\r\n')

mcsv = open('members.csv', 'w+')
mcsv.write('Created ' + str(d) + '\r\n\r\n')
mcsv.write('Member, Accounts\r\n')
for member in members:
    account_str = ''
    accounts = member.accounts
    for account in accounts:
        account_str += account.client_name + ', '

    mcsv.write(member.user.get_full_name() + ', ' + account_str + '\r\n')

bcsv = open('backups.csv', 'w+')
bcsv.write('Created ' + str(d))
for backup_period in backup_periods:
    bcsv.write('\r\n\r\n')
    bcsv.write(str(backup_period) + '\r\n')
    for backup in backup_period.backup_set.all():
        bcsv.write(str(backup) + '\r\n')
