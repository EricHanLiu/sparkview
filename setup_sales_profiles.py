import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client
from client_area.models import SalesProfile


def main():
    accounts = Client.objects.all()

    for account in accounts:
        profile, created = SalesProfile.objects.get_or_create(account=account)
        if not created:
            continue
        if account.status == 1:  # Active accounts only
            if account.has_seo:
                profile.seo_status = 1
            if account.has_cro:
                profile.cro_status = 1
            if account.has_ppc:
                profile.ppc_status = 1
        profile.save()

        print('created profile for ' + account.client_name)


main()
