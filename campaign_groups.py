import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from budget.models import CampaignGrouping
from tasks.campaign_group_tasks import update_campaigns_in_campaign_group


def main():
    groups = CampaignGrouping.objects.all()

    for group in groups:
        update_campaigns_in_campaign_group(group)


main()
