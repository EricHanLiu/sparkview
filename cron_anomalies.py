import os
import django
import gc
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import sys
from googleads import adwords
django.setup()
from django.conf import settings

from adwords_dashboard.cron_scripts import anomalies
from adwords_dashboard import models


def add_anomalies(anomaly, acc):

    account_7 = anomaly.get_account_stats_7_days()
    account_7 = anomaly.anomalies(account_7)

    account_14 = anomaly.get_account_stats_14_days()
    account_14 = anomaly.anomalies(account_14)

    campaign_7 = anomaly.get_campaign_stats_7_days()
    campaign_7 = anomaly.anomalies(campaign_7)

    campaign_14 = anomaly.get_campaign_stats_14_days()
    campaign_14 = anomaly.anomalies(campaign_14)

    if account_7 and account_14:
        if account_7[0]['Clicks'] == 0 or account_14[0]['Clicks'] == 0:
            acc_clicks = 0
        else:
            acc_clicks = (account_7[0]['Clicks'] / account_14[0]['Clicks']) * 100 - 100

        if account_7[0]['Impressions'] == 0 or account_14[0]['Impressions'] == 0:
            acc_impressions = 0
        else:
            acc_impressions = (account_7[0]['Impressions'] / account_14[0]['Impressions']) * 100 - 100

        if account_7[0]['CTR'] == 0 or account_14[0]['CTR'] == 0:
            acc_ctr = 0
        else:
            acc_ctr = ((account_7[0]['CTR'] / account_14[0]['CTR']) * 100) - 100

        if account_7[0]['Conversions'] == 0 or account_14[0]['Conversions'] == 0:
            acc_conversions = 0
        else:
            acc_conversions = (account_7[0]['Conversions'] / account_14[0]['Conversions']) * 100 - 100

        if account_7[0]['Avg. CPC'] == 0 or account_14[0]['Avg. CPC'] == 0:
            acc_cpc = 0
        else:
            acc_cpc = (account_7[0]['Avg. CPC'] / account_14[0]['Avg. CPC']) * 100 - 100

        if account_7[0]['Cost'] == 0 or account_14[0]['Cost'] == 0:
            acc_cost = 0
        else:
            acc_cost = (account_7[0]['Cost'] / account_14[0]['Cost']) * 100 - 100
        print(acc_cost)
        if account_7[0]['Cost / conv.'] == 0 or account_14[0]['Cost / conv.'] == 0:
            acc_cost_per_conv = 0
        else:
            acc_cost_per_conv = (account_7[0]['Cost / conv.'] / account_14[0]['Cost / conv.']) * 100 - 100

        if account_7[0]['Search Impr. share'] == 0 or account_14[0]['Search Impr. share'] == 0:
            acc_sis = 0
        else:
            acc_sis = (account_7[0]['Search Impr. share'] / account_14[0]['Search Impr. share']) * 100 - 100

        print('Built data..')
        models.Performance.objects.filter(account=acc, performance_type='ACCOUNT').delete()
        print('Dropped current items from Performance for current account')
        models.Performance.objects.create(account=acc, performance_type='ACCOUNT',
                                          clicks=acc_clicks, cost=acc_cost, impressions=acc_impressions, ctr=acc_ctr,
                                          conversions=acc_conversions, cpc=acc_cpc,
                                          cost_per_conversions=acc_cost_per_conv,
                                          search_impr_share=acc_sis)
        print('Added to DB - Account ' + acc.dependent_account_name)
    else:
        print('No data found. Added 0 to DB fields. [ACCOUNT]')
        models.Performance.objects.create(account=acc, performance_type='ACCOUNT', clicks=0, cost=0, impressions=0,
                                          ctr=0, conversions=0, cpc=0, cost_per_conversions=0, search_impr_share=0)

    if campaign_7 and campaign_14:
        models.Performance.objects.filter(account=acc, performance_type='CAMPAIGN').delete()
        print('Dropped current items from Performance table at campaign level')
        a = sorted(campaign_7, key=lambda k: k['Campaign ID'])
        b = sorted(campaign_14, key=lambda k: k['Campaign ID'])
        for x, y in zip(a, b):
            cmp_name = x['Campaign']
            cmp_id = x['Campaign ID']

            if x['Clicks'] == 0 or y['Clicks'] == 0:
                cmp_clicks = 0
            else:
                cmp_clicks = (x['Clicks'] / y['Clicks']) * 100 - 100

            if x['Impressions'] == 0 or y['Impressions'] == 0:
                cmp_impressions = 0
            else:
                cmp_impressions = (x['Impressions'] / y['Impressions']) * 100 - 100

            if x['CTR'] == 0 or y['CTR'] == 0:
                cmp_ctr = 0
            else:
                cmp_ctr = (x['CTR'] / y['CTR']) * 100 - 100

            if x['Conversions'] == 0 or y['Conversions'] == 0:
                cmp_conversions = 0
            else:
                cmp_conversions = (x['Conversions'] / y['Conversions']) * 100 - 100

            if x['Avg. CPC'] == 0 or y['Avg. CPC'] == 0:
                cmp_cpc = 0
            else:
                cmp_cpc = (x['Avg. CPC'] / y['Avg. CPC']) * 100 - 100

            if x['Cost'] == 0 or y['Cost'] == 0:
                cmp_cost = 0
            else:
                cmp_cost = (x['Cost'] / y['Cost']) * 100 - 100

            if x['Cost / conv.'] == 0 or y['Cost / conv.'] == 0:
                cmp_cost_per_conversions = 0
            else:
                cmp_cost_per_conversions = (x['Cost / conv.'] / y['Cost / conv.']) * 100 - 100
            if x['Search Impr. share'] == 0 or y['Search Impr. share'] == 0:
                cmp_sis = 0
            else:
                cmp_sis = (x['Search Impr. share'] / y['Search Impr. share']) * 100 - 100

            print('Built campaign data')

            models.Performance.objects.create(account=acc, performance_type='CAMPAIGN', campaign_name=cmp_name,
                                              campaign_id=cmp_id, clicks=cmp_clicks, cost=cmp_cost,
                                              impressions=cmp_impressions, ctr=cmp_ctr, conversions=cmp_conversions,
                                              cpc=cmp_cpc, cost_per_conversions=cmp_cost_per_conversions,
                                              search_impr_share=cmp_sis)

            print('Added to DB - Campaigns ' + cmp_name)
    else:
        models.Performance.objects.create(account=acc, performance_type='CAMPAIGN', clicks=0, cost=0, impressions=0,
                                          ctr=0, conversions=0, cpc=0, cost_per_conversions=0,
                                          search_impr_share=0)
        print('No data found. Added 0 to DB fields. [CMP]')


def main():
    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)

    accounts = models.DependentAccount.objects.all()
    if accounts:
        for account in accounts:
            try:
                anomaly = anomalies.Anomalies(adwords_client, account.dependent_account_id)
                anomaly.get_stats()
                print('Got stats..')
                add_anomalies(anomaly, account)
                print('Inserted data in DB')
                anomaly.cleanMemory()
                print('Cleaned junk...')
                print('Data added to DB for account ' + account.dependent_account_name)
            except KeyboardInterrupt:
                break
            except:
                print('Lamentably failed!!!')


if __name__ == '__main__':
    main()
