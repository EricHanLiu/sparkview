import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()

from client_area.models import AccountAllocatedHoursHistory, AccountHourRecord
from user_management.models import Member, MemberHourHistory

members = Member.objects.all()

# Change these to whatever month you want to go back to
# In production, this only works until November 2018 probably
year = 2019
month = 3

for member in members:
    actual_hour_records = AccountHourRecord.objects.filter(member=member, month=month, year=year, is_unpaid=False)
    actual_hours = 0.0
    for r in actual_hour_records:
        actual_hours += r.hours

    allocated_hours_records = AccountAllocatedHoursHistory.objects.filter(member=member, month=month, year=year)
    allocated_hours = 0.0
    for r in allocated_hours_records:
        allocated_hours += r.allocated_hours

    rec, created = MemberHourHistory.objects.get_or_create(member=member, year=year, month=month)

    if created:
        rec.allocated_hours = allocated_hours
        rec.actual_hours = actual_hours
        rec.save()

