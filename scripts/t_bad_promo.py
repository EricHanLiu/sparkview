import os
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from tasks.promo_tasks import get_bad_ads, get_bad_ad_group_ads
from adwords_dashboard.models import DependentAccount

d = DependentAccount.objects.get(dependent_account_id='2997298659')
get_bad_ad_group_ads(d.id)
