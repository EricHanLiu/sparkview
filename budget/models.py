from django.db import models
from adwords_dashboard import models as adwords_a
from bing_dashboard import models as bing_a
# from facebook_dashboard import models as fb

# Create your models here.


class Client(models.Model):

    client_id = models.AutoField(primary_key=True, default=1)
    client_name = models.CharField(max_length=255, default='None')
    adwords = models.ManyToManyField(adwords_a.DependentAccount, default=None)
    bing = models.ManyToManyField(bing_a.BingAccounts, default=None)
    # facebook = models.ManyToManyField(fb.FacebookAccount, on_delete=models.CASCADE)
    budget = models.IntegerField(default=0)
    current_spend = models.IntegerField(default=0)