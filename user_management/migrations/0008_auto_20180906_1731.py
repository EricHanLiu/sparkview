# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-06 17:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0007_auto_20180830_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='last_language_check',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_skill_check',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.RemoveField(
            model_name='member',
            name='team',
        ),
        migrations.AddField(
            model_name='member',
            name='team',
            field=models.ManyToManyField(blank=True, null=True, related_name='member_team', to='user_management.Team'),
        ),
    ]
