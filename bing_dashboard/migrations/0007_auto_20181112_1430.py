# Generated by Django 2.1.1 on 2018-11-12 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bing_dashboard', '0006_auto_20181107_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bingaccounts',
            name='assigned_am',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='bing_am', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bingaccounts',
            name='assigned_cm2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='bing_cm2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bingaccounts',
            name='assigned_cm3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='bing_cm3', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bingaccounts',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bingalerts',
            name='account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='bing_dashboard.BingAccounts'),
        ),
        migrations.AlterField(
            model_name='binganomalies',
            name='account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='bing_dashboard.BingAccounts'),
        ),
        migrations.AlterField(
            model_name='bingcampaign',
            name='account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='bing_dashboard.BingAccounts'),
        ),
    ]