from django.db import models


class Notification(models.Model):
    """
    These are notifications that a user will see in the top right hand corner of the interface
    """
    member = models.ForeignKey('user_management.Member',  models.DO_NOTHING, default=None, null=True)
    account = models.ForeignKey('budget.Client',  models.DO_NOTHING, default=None, null=True)
    message = models.CharField(max_length=999)
    link = models.URLField(max_length=499)
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.member.user.get_full_name + ' ' + self.message
