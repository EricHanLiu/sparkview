# Generated by Django 2.1.1 on 2019-08-26 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0092_client_onboarding_hours_allocated_updated_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='onboarding_hours_allocated_this_month_field',
            field=models.FloatField(default=0.0),
        ),
    ]
