from django.db import models
from budget.models import Client


class GoogleAnalyticsAuth(models.Model):
    """
    Store credentials for Google Analytics Auth
    """
    account = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, default=None)
    auth_string = models.CharField(max_length=99999, default='')

    def __str__(self):
        return self.account.client_name
