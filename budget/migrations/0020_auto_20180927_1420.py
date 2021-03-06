# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-27 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0019_auto_20180926_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='am1percent',
            field=models.FloatField(default=25.0),
        ),
        migrations.AddField(
            model_name='client',
            name='am2percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='am3percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='cm1percent',
            field=models.FloatField(default=75.0),
        ),
        migrations.AddField(
            model_name='client',
            name='cm2percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='cm3percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='seo1percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='seo2percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='seo3percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='strat1percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='strat2percent',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='strat3percent',
            field=models.FloatField(default=0),
        ),
    ]
