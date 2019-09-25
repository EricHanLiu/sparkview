import os
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from facebook_dashboard.models import FacebookCampaign


def main():
    campaign_name = input('Enter campaign name exactly: ')
    try:
        campaign_init = FacebookCampaign.objects.get(campaign_name=campaign_name)
    except FacebookCampaign.DoesNotExist:
        print('Error, cannot find this campaign')
        return

    for camp in FacebookCampaign.objects.filter(campaign_id=campaign_init.campaign_id):
        if camp.campaign_name != campaign_name:
            camp.delete()


main()
