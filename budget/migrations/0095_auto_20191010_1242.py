# Generated by Django 2.1.1 on 2019-10-10 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0094_merge_20190827_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='num_days_onboarding',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='num_times_flagged',
            field=models.IntegerField(default=0),
        ),
    ]