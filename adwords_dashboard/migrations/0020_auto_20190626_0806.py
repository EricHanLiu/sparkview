# Generated by Django 2.1.1 on 2019-06-26 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adwords_dashboard', '0019_campaignspenddaterange_spend_until_yesterday'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googlecampaignexclusion',
            name='campaign',
        ),
        migrations.DeleteModel(
            name='GoogleCampaignExclusion',
        ),
    ]