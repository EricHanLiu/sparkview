# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-11 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0012_auto_20180911_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='score0',
            field=models.ManyToManyField(blank=True, default=None, related_name='score0', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='score1',
            field=models.ManyToManyField(blank=True, default=None, related_name='score1', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='score2',
            field=models.ManyToManyField(blank=True, default=None, related_name='score2', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='score3',
            field=models.ManyToManyField(blank=True, default=None, related_name='score3', to='user_management.Member'),
        ),
    ]
