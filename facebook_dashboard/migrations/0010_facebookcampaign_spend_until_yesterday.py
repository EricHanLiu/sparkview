# Generated by Django 2.1.1 on 2019-06-25 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_dashboard', '0009_facebookcampaignexclusion'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebookcampaign',
            name='spend_until_yesterday',
            field=models.FloatField(default=0.0),
        ),
    ]