# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-27 16:21
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adwords_dashboard', '0001_initial'),
        ('facebook_dashboard', '0001_initial'),
        ('bing_dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget', models.FloatField(default=0)),
                ('network_type', models.CharField(default='ALL', max_length=255)),
                ('spend', models.FloatField(default=0)),
                ('adwords', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount')),
            ],
        ),
        migrations.CreateModel(
            name='CampaignGrouping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(default='', max_length=255)),
                ('group_by', models.CharField(default='', max_length=255)),
                ('budget', models.FloatField(default=0)),
                ('current_spend', models.FloatField(default=0)),
                ('adwords', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount')),
                ('aw_campaigns', models.ManyToManyField(blank=True, related_name='aw_campaigns', to='adwords_dashboard.Campaign')),
                ('bing', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bing_dashboard.BingAccounts')),
                ('bing_campaigns', models.ManyToManyField(blank=True, related_name='bing_campaigns', to='bing_dashboard.BingCampaign')),
                ('facebook', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='facebook_dashboard.FacebookAccount')),
                ('fb_campaigns', models.ManyToManyField(blank=True, related_name='facebook_campaigns', to='facebook_dashboard.FacebookCampaign')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(default='None', max_length=255)),
                ('current_spend', models.FloatField(default=0)),
                ('yesterday_spend', models.FloatField(default=0)),
                ('aw_spend', models.FloatField(default=0)),
                ('bing_spend', models.FloatField(default=0)),
                ('fb_spend', models.FloatField(default=0)),
                ('budget', models.FloatField(default=0)),
                ('target_spend', models.FloatField(default=0)),
                ('has_gts', models.BooleanField(default=False)),
                ('has_budget', models.BooleanField(default=False)),
                ('aw_budget', models.FloatField(default=0)),
                ('bing_budget', models.FloatField(default=0)),
                ('fb_budget', models.FloatField(default=0)),
                ('adwords', models.ManyToManyField(blank=True, related_name='adwords', to='adwords_dashboard.DependentAccount')),
                ('bing', models.ManyToManyField(blank=True, related_name='bing', to='bing_dashboard.BingAccounts')),
                ('facebook', models.ManyToManyField(blank=True, related_name='facebook', to='facebook_dashboard.FacebookAccount')),
            ],
        ),
        migrations.CreateModel(
            name='ClientCData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aw_budget', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('aw_projected', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('aw_spend', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('bing_budget', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('bing_projected', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('bing_spend', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('fb_budget', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('fb_projected', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('fb_spend', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
            ],
        ),
        migrations.CreateModel(
            name='ClientHist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(default='None', max_length=255)),
                ('hist_spend', models.FloatField(default=0)),
                ('hist_aw_spend', models.FloatField(default=0)),
                ('hist_bing_spend', models.FloatField(default=0)),
                ('hist_fb_spend', models.FloatField(default=0)),
                ('hist_budget', models.FloatField(default=0)),
                ('hist_aw_budget', models.FloatField(default=0)),
                ('hist_bing_budget', models.FloatField(default=0)),
                ('hist_fb_budget', models.FloatField(default=0)),
                ('hist_adwords', models.ManyToManyField(blank=True, related_name='hist_adwords', to='adwords_dashboard.DependentAccount')),
                ('hist_bing', models.ManyToManyField(blank=True, related_name='hist_bing', to='bing_dashboard.BingAccounts')),
                ('hist_facebook', models.ManyToManyField(blank=True, related_name='hist_facebook', to='facebook_dashboard.FacebookAccount')),
            ],
        ),
        migrations.CreateModel(
            name='FlightBudget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget', models.FloatField(default=0)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('current_spend', models.FloatField(default=0)),
                ('adwords_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount')),
                ('bing_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bing_dashboard.BingAccounts')),
                ('facebook_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='facebook_dashboard.FacebookAccount')),
            ],
        ),
    ]