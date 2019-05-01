import os
import csv
import django
from datetime import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from budget.models import Client
from user_management.models import Member, Incident, IncidentReason


file = open('oopsreports.csv', 'r')
reader = csv.reader(file, delimiter=',')
count = 0
for row in reader:
    # skip first line
    if count < 2:
        count += 1
        continue

    # Add incident
    incident = Incident()

    email = row[1]
    name = email.split('@')[0].capitalize()
    print(name)
    if name == "Genevieve":
        incident.reporter = Member.objects.get(user__first_name='Geneviève')
    elif name != "Arnaud":  # probably old member no longer exists
        incident.reporter = Member.objects.get(user__first_name__contains=name)
    incident.service = 6  # none
    try:
        incident.account = Client.objects.get(client_name=row[17])
    except Client.DoesNotExist:
        incident.account = None
    date = (row[16] if row[16] is not '' else row[0]).split('/')  # get date into array
    formatted_date = date[2][:4] + '-' + date[0] + '-' + date[1]
    incident.date = formatted_date
    timestamp = datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S")
    incident.timestamp = timestamp
    incident.save()

    members = []
    members.append(row[5])
    if row[18] != '':
        members.append(row[18])
    member_objects = Member.objects.filter(user__first_name__in=members)
    incident.members.set(member_objects)

    incident.description = row[15]  # additional comments

    # parse incident type
    issue_str = row[2].lower()
    incident_reason = IncidentReason.objects.get(name__contains=issue_str)
    incident.issue = incident_reason

    # parse platform type
    platform = row[9].lower()
    if platform == 'adwords':
        incident.platform = 0
    elif platform == 'facebook':
        incident.platform = 1
    elif platform == 'bing':
        incident.platform = 2
    else:
        incident.platform = 3

    incident.client_aware = (row[7].lower() == 'yes')
    incident.client_at_risk = (row[12].lower() == 'yes')  # maybes will be counted as no
    incident.justification = row[14]

    incident.save()

print('Success')
