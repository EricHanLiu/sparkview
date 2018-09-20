from django.db import models

from user_management.models import Member


class ParentClient(models.Model):
    """
    This is really what should be considered a client. It can have many accounts under it.
    """
    pass


class Service(models.Model):
    name = models.CharField(max_length=255, default='No name')

    def __str__(self):
        return self.name


class Industry(models.Model):
    name = models.CharField(max_length=255, default='None')

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=255, default='None')

    def __str__(self):
        return self.name


class ClientType(models.Model):
    name = models.CharField(max_length=255, default='None')

    def __str__(self):
        return self.name


class ClientContact(models.Model):
     name  = models.CharField(max_length=255, default='None')
     email = models.EmailField(max_length=255, default='None')
