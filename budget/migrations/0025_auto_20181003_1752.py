# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-03 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0024_client_payment_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='allocated_ppc_buffer',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='client',
            name='allocated_ppc_override',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='client',
            name='status',
            field=models.IntegerField(choices=[(0, 'Onboarding'), (1, 'Active'), (2, 'Inactive'), (3, 'Lost')], default=0),
        ),
    ]
