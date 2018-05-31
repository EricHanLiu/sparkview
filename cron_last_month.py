import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from budget import models



def main():

    clients = models.Client.objects.all()
    models.ClientHist.objects.all().delete()
    for client in clients:

        hist_client = models.ClientHist.objects.create(client_name=client.client_name,
                                                       hist_spend=client.current_spend, hist_aw_spend=client.aw_spend,
                                                       hist_bing_spend=client.bing_spend,
                                                       hist_budget=client.budget, hist_aw_budget=client.aw_budget,
                                                       hist_bing_budget=client.bing_budget)

        for aw in client.adwords.all():
            aw.hist_spend = aw.current_spend
            aw.hist_budget = aw.desired_spend
            aw.save()
            hist_client.hist_adwords.add(aw)
            hist_client.save()

        for bing in client.bing.all():
            bing.hist_spend = bing.current_spend
            bing.hist_budget = bing.desired_spend
            bing.save()
            hist_client.hist_bing.add(bing)
            hist_client.save()

        for facebook in client.facebook.all():
            facebook.hist_spend = facebook.current_spend
            facebook.hist_budget = facebook.desired_spend
            facebook.save()
            hist_client.hist_facebook.add(facebook)
            hist_client.save()

        print('Client '+ client.client_name +' copied to ClientHist.')


if __name__ == '__main__':
    main()
