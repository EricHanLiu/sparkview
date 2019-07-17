from budget.models import Client


def ppc_active_accounts_for_platform(platform):
    clients = Client.objects.filter(salesprofile__ppc_status=1)
    # flat_list = [item for sublist in l for item in sublist]
    accounts = [acc for client in clients for acc in getattr(client, platform).all()]
    return list(set(accounts))  # remove duplicates


def active_adwords_accounts():
    return ppc_active_accounts_for_platform('adwords')


def active_facebook_accounts():
    return ppc_active_accounts_for_platform('facebook')


def active_bing_accounts():
    return ppc_active_accounts_for_platform('bing')
