from django.db import models

from budget.models import Client
from user_management.models import Member


class Service(models.Model):
    name = models.CharField(max_length=255, default='No name')

    def __str__(self):
        return self.name


class MemberClientRelationshipType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class MemberClientRelationship(models.Model):
    relationship = models.ForeignKey(MemberClientRelationshipType, on_delete=models.CASCADE, default=None)
    client       = models.ForeignKey(Client, on_delete=models.CASCADE, default=None)
    member       = models.ForeignKey(Member, on_delete=models.CASCADE, default=None)

    class Meta:
        unique_together = ('relationship', 'client')
