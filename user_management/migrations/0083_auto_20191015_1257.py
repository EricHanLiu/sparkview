# Generated by Django 2.1.1 on 2019-10-15 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0082_memberhourhistory_total_buffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberhourhistory',
            name='num_active_accounts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='memberhourhistory',
            name='num_onboarding_accounts',
            field=models.IntegerField(default=0),
        ),
    ]
