# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-29 15:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0034_auto_20181025_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='star_flag',
            field=models.BooleanField(default=False),
        ),
    ]