# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-27 16:19
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bing_dashboard', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Adgroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adgroup_id', models.CharField(default='None', max_length=255)),
                ('adgroup_name', models.CharField(default='None', max_length=255)),
                ('adgroup_cost', models.FloatField(default=0)),
                ('adgroup_budget', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dependent_account_id', models.CharField(max_length=255)),
                ('alert_type', models.CharField(max_length=255)),
                ('alert_reason', models.CharField(max_length=255)),
                ('ad_group_id', models.CharField(default='None', max_length=255)),
                ('ad_group_name', models.CharField(default='None', max_length=255)),
                ('keyWordText', models.TextField(default='None')),
                ('ad_headline', models.TextField(default='None')),
                ('campaign_id', models.CharField(default='None', max_length=255)),
                ('campaignName', models.CharField(default='None', max_length=255)),
                ('keyword_match_type', models.CharField(default='None', max_length=255)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['created_time', 'updated_time'],
            },
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_id', models.CharField(default='None', max_length=255)),
                ('campaign_name', models.CharField(default='None', max_length=255)),
                ('campaign_cost', models.FloatField(default=0)),
                ('campaign_budget', models.FloatField(default=0)),
                ('campaign_status', models.CharField(default='None', max_length=255)),
                ('campaign_serving_status', models.CharField(default='None', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CampaignStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dependent_account_id', models.CharField(max_length=255)),
                ('campaign_id', models.CharField(default='None', max_length=255)),
                ('campaign_name', models.CharField(max_length=255)),
                ('ad_group_id', models.CharField(max_length=255)),
                ('ad_group_name', models.TextField(default='None')),
                ('ad_url', models.TextField(default='None')),
                ('ad_headline', models.TextField(default='None')),
                ('ad_url_code', models.TextField()),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['created_time', 'updated_time'],
            },
        ),
        migrations.CreateModel(
            name='DependentAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manager_account', models.CharField(default='None', max_length=255)),
                ('dependent_account_id', models.CharField(max_length=255)),
                ('dependent_account_name', models.CharField(default='None', max_length=255)),
                ('dependent_OVU', models.IntegerField(default=0)),
                ('desired_spend', models.IntegerField(default=0)),
                ('current_spend', models.FloatField(default=0)),
                ('segmented_spend', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('trends', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('qscore_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('channel', models.CharField(default='None', max_length=255)),
                ('hist_spend', models.FloatField(default=0)),
                ('hist_budget', models.FloatField(default=0)),
                ('ds1', models.IntegerField(default=0)),
                ('ds2', models.IntegerField(default=0)),
                ('ds3', models.IntegerField(default=0)),
                ('ds4', models.IntegerField(default=0)),
                ('ds5', models.IntegerField(default=0)),
                ('ds6', models.IntegerField(default=0)),
                ('yesterday_spend', models.FloatField(default=0)),
                ('estimated_spend', models.FloatField(default=0)),
                ('qs_score', models.FloatField(default=0)),
                ('ctr_score', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('cvr_score', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('cpa_score', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('roi_score', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('cost_score', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('conversions_score', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('trends_score', models.FloatField(default=0)),
                ('dads_score', models.FloatField(default=0)),
                ('changed_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('changed_score', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('nr_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('nr_score', models.FloatField(default=0)),
                ('account_score', models.FloatField(default=0)),
                ('weekly_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('hist_qs', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('assigned', models.BooleanField(default=False)),
                ('blacklisted', models.BooleanField(default=False)),
                ('protected', models.BooleanField(default=False)),
                ('assigned_am', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aw_am', to=settings.AUTH_USER_MODEL)),
                ('assigned_cm2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aw_cm2', to=settings.AUTH_USER_MODEL)),
                ('assigned_cm3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aw_cm3', to=settings.AUTH_USER_MODEL)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_time', 'updated_time'],
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label_id', models.CharField(default='None', max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('label_type', models.CharField(default='None', max_length=255)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount')),
                ('accounts', models.ManyToManyField(blank=True, related_name='lbl_assigned_aw', to='adwords_dashboard.DependentAccount')),
                ('adgroups', models.ManyToManyField(blank=True, related_name='lbl_assigned_cmp', to='adwords_dashboard.Adgroup')),
                ('campaigns', models.ManyToManyField(blank=True, related_name='lbl_assigned_cmp', to='adwords_dashboard.Campaign')),
            ],
            options={
                'ordering': ['created_time', 'updated_time'],
            },
        ),
        migrations.CreateModel(
            name='ManagerAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manager_account_id', models.CharField(max_length=255)),
                ('manager_account_name', models.CharField(max_length=255)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['created_time', 'updated_time'],
            },
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('performance_type', models.CharField(max_length=255)),
                ('campaign_id', models.CharField(default='None', max_length=255)),
                ('campaign_name', models.CharField(default='None', max_length=255)),
                ('cpc', models.CharField(max_length=255)),
                ('clicks', models.CharField(max_length=255)),
                ('conversions', models.CharField(max_length=255)),
                ('cost', models.CharField(default=0, max_length=255)),
                ('cost_per_conversions', models.CharField(max_length=255)),
                ('ctr', models.CharField(max_length=255)),
                ('impressions', models.CharField(max_length=255)),
                ('search_impr_share', models.CharField(max_length=255)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount')),
            ],
            options={
                'ordering': ['created_time', 'updated_time'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('adwords', models.ManyToManyField(blank=True, related_name='aw_accs', to='adwords_dashboard.DependentAccount')),
                ('bing', models.ManyToManyField(blank=True, related_name='bing_accs', to='bing_dashboard.BingAccounts')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', 'created_time', 'updated_time'],
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AddField(
            model_name='adgroup',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AddField(
            model_name='adgroup',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='adwords_dashboard.Campaign'),
        ),
    ]