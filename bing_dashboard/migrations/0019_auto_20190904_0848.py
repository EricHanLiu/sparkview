# Generated by Django 2.1.1 on 2019-09-04 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bing_dashboard', '0018_auto_20190709_0652'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bingcampaign',
            unique_together={('campaign_id', 'campaign_name')},
        ),
    ]
