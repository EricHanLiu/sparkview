from django.db import models
from budget.models import Client
from adwords_dashboard.models import DependentAccount
from facebook_dashboard.models import FacebookAccount
from bing_dashboard.models import BingAccounts


class Healthcheck(models.Model):
    """
    Healthcheck
    """
    AD_NETWORK_CHOICES = [(0, 'Google Ads'), (1, 'Facebook'), (2, 'Bing')]

    account = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, default=None)
    ad_network = models.IntegerField(default=0, choices=AD_NETWORK_CHOICES)
    aw_account = models.ForeignKey(DependentAccount, on_delete=models.CASCADE, null=True, default=None)
    fb_account = models.ForeignKey(FacebookAccount, on_delete=models.CASCADE, null=True, default=None)
    bing_account = models.ForeignKey(BingAccounts, on_delete=models.CASCADE, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.account) + ' ' + str(self.created_at)
