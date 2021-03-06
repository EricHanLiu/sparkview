# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-26 18:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0011_auto_20180925_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagementFeeInterval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feeStyle', models.IntegerField(choices=[(0, '%'), (1, '$')], default=0)),
                ('fee', models.FloatField(default=0)),
                ('lowerBound', models.FloatField(default=0)),
                ('upperBound', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ManagementFeesStructure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initialFee', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('feeStructure', models.ManyToManyField(blank=True, to='client_area.ManagementFeeInterval')),
            ],
        ),
    ]
