import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from django.shortcuts import get_object_or_404
from budget.models import Client
from django.contrib.auth.models import User
from client_area.models import ParentClient, Industry, ClientContact, Language, ClientType
from user_management.models import Team, Member
from datetime import datetime
from datetime import date


file = open('bpops.csv', 'r')
reader = csv.reader(file, delimiter=',')
counter = 0
for row in reader:
    counter += 1
    if (counter <= 2):
        continue

    # Add account
    account = Client()

    # account name
    name = row[1]
    if (name == ''):
        continue

    account.client_name = name

    # parent client
    client_name = row[0]
    if (client_name != ''):
        client, created = ParentClient.objects.get_or_create(name=client_name)
        account.parentClient = client

    url = row[2]
    account.url = url

    # industry
    industry_name = row[3]
    if (industry_name != ''):
        industry = Industry.objects.get_or_create(name=industry_name)
        account.industry = industry[0]

    # client type
    client_type_name = row[7]
    if (client_type_name != ''):
        client_type = ClientType.objects.get_or_create(name=client_type_name)
        account.clientType = client_type[0]

    tier = row[8]
    if (tier == ''):
        tier = 1
    account.tier = int(tier)

    sold_by_name = row[9]
    if (sold_by_name != ''):
        try:
            user = User.objects.get(first_name=sold_by_name)
            sold_by = Member.objects.get(user=user)
            account.soldBy = sold_by
        except:
            print('No user named ' + sold_by_name)

    account.save()

    # client contact
    client_contact_name = row[4]
    client_contact_email = row[5]
    if (client_contact_name != '' or client_contact_email != ''):
        client_contact, created = ClientContact.objects.get_or_create(name=client_contact_name, email=client_contact_email)
        account.contactInfo.set([client_contact])

    # language
    language_name = row[6]
    if (language_name != ''):
        language = Language.objects.get_or_create(name=language_name)
        account.language.set([language[0]])

    statusDict = {
        'LAUNCH' : 0,
        'ACTIVE' : 1,
        'INACTIVE': 2,
        'LOST' : 3
    }

    status_string = row[24]
    status_number = statusDict.get(status_string, 0)

    account.status = status_number

    payment_type_dict = {
        'MRR' : 0,
        'OT'  : 1
    }

    payment_schedule = payment_type_dict.get(row[27], 0)
    account.payment_schedule = payment_schedule

    team_name = row[28]
    if (team_name != ''):
        team = Team.objects.get_or_create(name=team_name)
        account.team.set([team[0]])

    # SEO and CRO
    seo_hours = row[33]
    cro_hours = row[34]

    # SEO first
    if (seo_hours != '' and float(seo_hours) != 0.0):
        account.has_seo = True
        account.seo_hours = float(seo_hours)
    # CRO
    if (cro_hours != '' and float(cro_hours) != 0.0):
        account.has_cro = True
        account.cro_hours = float(cro_hours)

    am1 = row[42]
    cm1 = row[43]
    cm2 = row[44]
    seo = row[45]
    strat = row[46]

    # do am first
    if (am1 != ''):
        try:
            am_user = User.objects.get(first_name=am1)
            am_obj = Member.objects.get(user=am_user)
            account.am1 = am_obj
        except:
            print('No am named ' + am1)

    # do cms
    if (cm1 != ''):
        try:
            cm1_user = User.objects.get(first_name=cm1)
            cm1_obj = Member.objects.get(user=cm1_user)
            account.cm1 = cm1_obj
        except:
            print('No cm1 named ' + cm1)

    if (cm2 != ''):
        try:
            cm2_user = User.objects.get(first_name=cm2)
            cm2_obj = Member.objects.get(user=cm2_user)
            account.cm2 = cm2_obj
        except:
            print('No cm2 named ' + cm2)

    if (seo != ''):
        try:
            seo_user = User.objects.get(first_name=seo)
            seo_obj = Member.objects.get(user=seo_user)
            account.seo1 = seo_obj
        except:
            print('No seo named ' + seo)

    if (strat != ''):
        try:
            strat_user = User.objects.get(first_name=strat)
            strat_obj = Member.objects.get(user=strat_user)
            account.strat1 = strat_obj
        except:
            print('No strat named ' + strat)

    account.save()
    print('Account ' + account.client_name + ' created!')
