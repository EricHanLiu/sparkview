import gc
import os
import sys
from googleads import adwords

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from adwords_dashboard import models
from django.conf import settings

from adwords_dashboard.cron_scripts import alert_system

import logging

# logger_alerts = logging.getLogger('dashboard_alerts')


def add_Alerts(alerts):
    disapprovedAds = alerts.disapprovedCheck()
    # duplicates = alerts.duplicateCheck()
    # emptyAds = alerts.emptyAdsCheck()
    # emptyAdgroups = alerts.emptyAdGroup()
    total_alerts = []
    # if duplicates:
    #     for keyword in duplicates:
    #         alert_type = 'DUPLICATE'
    #         alert_reason = 'DUPLICATE KEYWORD'
    #         adgroupId = keyword.adGroupId if hasattr(keyword, 'adGroupId') else 'Not Found'
    #         keyword_txt = keyword.criterion.text if hasattr(keyword.criterion, 'text') else 'Not Found'
    #         keyword_matchType = keyword.criterion.matchType if hasattr(keyword.criterion, 'matchType') else 'Not Found'
    #         adgroupName = [adgroup.name for adgroup in alerts.adgroups if str(adgroup.id) == adgroupId][0] \
    #             if [adgroup for adgroup in alerts.adgroups if str(adgroup.id) == adgroupId] else 'Unknown'
    #         currents = models.Alert.objects.filter(keyWordText=keyword_txt, keyword_match_type=keyword_matchType,
    #                                                ad_group_id=adgroupId)
    #         if not currents:
    #             total_alerts.append(models.Alert(
    #                 dependent_account_id=alerts.customerId,
    #                 alert_type=alert_type,
    #                 alert_reason=alert_reason,
    #                 ad_group_id=adgroupId,
    #                 ad_group_name=adgroupName,
    #                 keyWordText=keyword_txt,
    #                 keyword_match_type=keyword_matchType))

    if disapprovedAds:

        for adGroupAd in disapprovedAds:

            alert_type = 'DISAPPROVED_AD'
            alert_reason = str(adGroupAd.policySummary['policyTopicEntries'][0]['policyTopicName']) \
                if 'policyTopicEntries' in adGroupAd.policySummary and adGroupAd.policySummary[
                'policyTopicEntries'] else 'Unknown'
            adgroupId = str(adGroupAd.adGroupId) if hasattr(adGroupAd, 'adGroupId') else 'Not Found'
            headline = adGroupAd.ad.headlinePart1 if hasattr(adGroupAd.ad, 'headlinePart1') else 'Not Found'
            adgroupName = [adgroup.name for adgroup in alerts.adgroups if str(adgroup.id) == adgroupId][0] \
                if [adgroup for adgroup in alerts.adgroups if str(adgroup.id) == adgroupId] else 'Unknown'

            currents = models.Alert.objects.filter(ad_headline=headline, alert_type=alert_type,
                                                   alert_reason=alert_reason)
            if not currents:
                total_alerts.append(models.Alert(
                    dependent_account_id=alerts.customerId,
                    alert_type=alert_type,
                    alert_reason=alert_reason,
                    ad_group_id=adgroupId,
                    ad_group_name=adgroupName,
                    ad_headline=headline))

    # if emptyAds:
    #
    #     for adgroup in emptyAds:
    #         alert_type = "EMPTY_ADGROUPS"
    #         alert_reason = "NO ADS"
    #         adGroupId = str(adgroup.id)
    #         campaignId = str(adgroup.campaignId)
    #         adGroupName = adgroup.name
    #         campaignName = adgroup.campaignName
    #         currents = models.Alert.objects.filter(ad_group_id=adGroupId, alert_type=alert_type, campaign_id=campaignId)
    #         if not currents:
    #             total_alerts.append(models.Alert(
    #                 dependent_account_id=alerts.customerId,
    #                 alert_type=alert_type,
    #                 alert_reason=alert_reason,
    #                 ad_group_id=adGroupId,
    #                 campaign_id=campaignId,
    #                 ad_group_name=adGroupName,
    #                 campaignName=campaignName))
    #
    # if emptyAdgroups:
    #
    #     for campaign in emptyAdgroups:
    #         alert_type = "EMPTY_CAMPAIGNS"
    #         alert_reason = "NO ADGROUPS"
    #         campaignId = str(campaign.id)
    #         campaignName = campaign.name
    #         currents = models.Alert.objects.filter(campaign_id=campaignId, alert_type=alert_type)
    #         if not currents:
    #             total_alerts.append(models.Alert(
    #                 dependent_account_id=alerts.customerId,
    #                 alert_type=alert_type,
    #                 alert_reason=alert_reason,
    #                 campaign_id=campaignId,
    #                 campaignName=campaignName))

    return total_alerts


def main():
    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    accounts = models.DependentAccount.objects.filter(blacklisted=False)
    for account in accounts:
        try:
            alerts = alert_system.AlertSystem(client, account.dependent_account_id)
            alerts.buildAlerts()

            total_alerts = add_Alerts(alerts)
            print(len(total_alerts))
            models.Alert.objects.filter(dependent_account_id=account.dependent_account_id).delete()
            if len(total_alerts) > 0:
                models.Alert.objects.bulk_create(total_alerts)
            alerts.cleanMemory()
            print('COOL!')

        except:
            print('Failed for account ' + str(account.dependent_account_id))
    # time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # logger_alerts.info(time_now + " - CRON SCRIPT FINISHED FOR ACCOUNT %s [INFO]" % acc_id)


if __name__ == '__main__':
    main()
