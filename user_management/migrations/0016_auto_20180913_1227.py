# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-13 12:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0015_auto_20180912_1240'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='skillentry',
            unique_together=set([('skill', 'member')]),
        ),
    ]
