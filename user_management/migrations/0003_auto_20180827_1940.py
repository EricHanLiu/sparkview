# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-27 19:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_auto_20180827_1926'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='department',
        ),
        migrations.AddField(
            model_name='member',
            name='team',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='user_management.Team'),
        ),
    ]
