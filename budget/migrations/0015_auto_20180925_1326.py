# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-25 13:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0014_auto_20180924_1317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientchanges',
            name='client',
        ),
        migrations.RemoveField(
            model_name='clientchanges',
            name='member',
        ),
        migrations.DeleteModel(
            name='ClientChanges',
        ),
    ]