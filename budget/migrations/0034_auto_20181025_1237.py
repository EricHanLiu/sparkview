# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-25 12:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0033_auto_20181023_1426'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaigngrouping',
            name='current_spend',
        ),
        migrations.AddField(
            model_name='campaigngrouping',
            name='aw_spend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='campaigngrouping',
            name='aw_yspend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='campaigngrouping',
            name='bing_spend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='campaigngrouping',
            name='bing_yspend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='campaigngrouping',
            name='fb_spend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='campaigngrouping',
            name='fb_yspend',
            field=models.FloatField(default=0),
        ),
    ]
