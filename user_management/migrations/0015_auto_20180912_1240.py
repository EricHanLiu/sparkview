# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-12 12:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0014_skillentry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skill',
            name='score0',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='score1',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='score2',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='score3',
        ),
    ]