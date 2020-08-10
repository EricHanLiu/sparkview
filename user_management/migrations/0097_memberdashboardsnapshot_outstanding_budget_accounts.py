# Generated by Django 2.1.1 on 2019-11-12 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0098_client_region'),
        ('user_management', '0096_remove_memberdashboardsnapshot_outstanding_budget_accounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberdashboardsnapshot',
            name='outstanding_budget_accounts',
            field=models.ManyToManyField(related_name='outstanding_budget_accounts', to='budget.Client'),
        ),
    ]