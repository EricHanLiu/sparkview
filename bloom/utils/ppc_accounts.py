from budget.models import Client


def ppc_active_accounts_for_platform(platform):
    clients = Client.objects.filter(salesprofile__ppc_status=1)
    # flat_list = [item for sublist in l for item in sublist]
    accounts = [acc for client in clients for acc in getattr(client, platform).all()]
    return list(set(accounts))  # remove duplicates
