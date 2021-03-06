# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-09 12:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0027_auto_20181004_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='clientType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_type', to='client_area.ClientType'),
        ),
        migrations.AlterField(
            model_name='client',
            name='contactInfo',
            field=models.ManyToManyField(blank=True, related_name='client_contact', to='client_area.ClientContact'),
        ),
        migrations.AlterField(
            model_name='client',
            name='currency',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='client',
            name='industry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='industry', to='client_area.Industry'),
        ),
    ]
