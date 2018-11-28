import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from budget.models import Client
from client_area.models import ClientType

clients = Client.objects.all()
client_types = ClientType.objects.all()

"""
This script will attempt to set older accounts to ecomm or lead gen (only two options we're going with for now)
"""
for client in clients:
    client.clientType = None
    client.save()
