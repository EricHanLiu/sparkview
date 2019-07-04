# Generated by Django 2.1.1 on 2019-06-19 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_dashboard', '0006_auto_20190104_0950'),
        ('adwords_dashboard', '0014_delete_campaignstat'),
        ('bing_dashboard', '0008_auto_20190104_0950'),
        ('budget', '0070_budget'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='aw_campaigns',
            field=models.ManyToManyField(blank=True, related_name='budget_aw_campaigns', to='adwords_dashboard.Campaign'),
        ),
        migrations.AddField(
            model_name='budget',
            name='aw_spend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='budget',
            name='aw_yspend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='budget',
            name='bing_campaigns',
            field=models.ManyToManyField(blank=True, related_name='budget_bing_campaigns', to='bing_dashboard.BingCampaign'),
        ),
        migrations.AddField(
            model_name='budget',
            name='bing_spend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='budget',
            name='bing_yspend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='budget',
            name='budget',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='budget',
            name='fb_campaigns',
            field=models.ManyToManyField(blank=True, related_name='budget_facebook_campaigns', to='facebook_dashboard.FacebookCampaign'),
        ),
        migrations.AddField(
            model_name='budget',
            name='fb_spend',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='budget',
            name='fb_yspend',
            field=models.FloatField(default=0),
        ),
    ]