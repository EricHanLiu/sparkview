# Generated by Django 2.1.1 on 2019-09-25 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bing_dashboard', '0021_auto_20190924_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='binganomalies',
            name='campaign_id',
            field=models.CharField(default='None', max_length=255),
        ),
    ]