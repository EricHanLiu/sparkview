# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-11 19:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0013_clientcontact_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='managementfeesstructure',
            name='name',
            field=models.CharField(default='No Name Fee Structure', max_length=255),
        ),
    ]
