# Generated by Django 2.1.1 on 2019-07-09 11:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_dashboard', '0017_facebookcampaignspenddaterange_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookaccount',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='facebookaccount',
            name='segmented_spend',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='facebookaccount',
            name='trends',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
