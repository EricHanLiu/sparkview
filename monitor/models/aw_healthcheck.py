from django.db import models
from budget.models import Client
from adwords_dashboard.models import DependentAccount


class GoogleAdsHealthcheck(models.Model):
    """
    Google Ads Healthcheck
    """
    account = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, default=None)
    aw_account = models.ForeignKey(DependentAccount, on_delete=models.CASCADE, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.account) + ' ' + str(self.created_at)
