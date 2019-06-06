import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from tasks.promo_tasks import get_bad_ads

get_bad_ads('4820718882')
