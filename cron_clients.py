import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from budget import models


def main():

    clients = models.Client.objects.all()
    for client in clients:
        client.budget = 0
        client.current_spend = 0
        client.aw_spend = 0
        client.bing_spend = 0
        client.yesterday_spend = 0
        client.save()

        adwords = client.adwords.all()
        for a in adwords:
            client.budget += a.desired_spend
            client.current_spend += a.current_spend
            client.aw_spend += a.current_spend
            client.yesterday_spend += a.yesterday_spend

        bing = client.bing.all()
        for b in bing:
            client.budget += b.desired_spend
            client.current_spend += b.current_spend
            client.bing_spend += b.current_spend
            client.yesterday_spend += b.yesterday_spend

        client.save()
        print('Updated current spend for client ' + client.client_name)

if __name__ == '__main__':
    main()