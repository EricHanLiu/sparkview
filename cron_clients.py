import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from budget import models


def main():

    clients = models.Client.objects.all()
    for client in clients:
        client.current_spend = 0
        client.save()

        adwords = client.adwords.all()
        for a in adwords:
            client.current_spend += a.current_spend

        bing = client.bing.all()
        for b in bing:
            client.current_spend += b.current_spend

        client.save()
        print('Updated current spend for client ' + client.client_name)

if __name__ == '__main__':
    main()