from django.db import models
from budget.models import Client


class Healthcheck(models.Model):
    """
    Healthcheck
    """
    account = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
