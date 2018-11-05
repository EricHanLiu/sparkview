# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-06 12:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0007_auto_20180830_1340'),
        ('budget', '0005_auto_20180905_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team', to='user_management.Team'),
        ),
        migrations.AddField(
            model_name='clientchanges',
            name='dateTime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='clientchanges',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_management.Member'),
        ),
    ]
