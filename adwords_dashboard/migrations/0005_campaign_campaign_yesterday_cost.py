# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-25 12:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adwords_dashboard', '0004_dependentaccount_ch_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='campaign_yesterday_cost',
            field=models.FloatField(default=0),
        ),
    ]