# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-04 18:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0026_auto_20181003_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='allocated_ppc_override',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='managementFee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='client_area.ManagementFeesStructure'),
        ),
        migrations.AlterField(
            model_name='client',
            name='management_fee_override',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]