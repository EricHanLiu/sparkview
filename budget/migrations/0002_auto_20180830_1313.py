# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-30 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaigngrouping',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='campaigngrouping',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
