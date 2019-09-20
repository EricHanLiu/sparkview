from django.db import models
from monitor.constants import HEALTH_STATUSES


class GoogleBadSubstringCheck(models.Model):
    """
    Instance of bad substring checking
    """
    healthcheck = models.ForeignKey('monitor.GoogleAdsHealthcheck', on_delete=models.CASCADE, null=True, default=None)
    status = models.IntegerField(default=1, choices=HEALTH_STATUSES)

    def __str__(self):
        return str(self.healthcheck)
