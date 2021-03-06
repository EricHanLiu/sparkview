# Generated by Django 2.1.1 on 2019-11-12 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_area', '0096_auto_20191112_0925'),
        ('user_management', '0094_auto_20191112_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberdashboardsnapshot',
            name='new_accounts',
            field=models.ManyToManyField(related_name='new_accounts', to='client_area.ClientDashboardSnapshot'),
        ),
        migrations.AddField(
            model_name='memberdashboardsnapshot',
            name='outstanding_budget_accounts',
            field=models.ManyToManyField(related_name='outstanding_budget_accounts', to='client_area.ClientDashboardSnapshot'),
        ),
    ]
