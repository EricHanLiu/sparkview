# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-01 17:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0021_auto_20180927_1420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='buffer_buffer_percentage',
        ),
        migrations.RemoveField(
            model_name='member',
            name='buffer_hours_available',
        ),
        migrations.AlterField(
            model_name='member',
            name='buffer_internal_percentage',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='buffer_learning_percentage',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='buffer_planning_percentage',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='buffer_sales_percentage',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='buffer_seniority_percentage',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='buffer_total_percentage',
            field=models.FloatField(blank=True, default=100, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='buffer_trainers_percentage',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]