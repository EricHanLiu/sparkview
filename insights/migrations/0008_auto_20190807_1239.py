# Generated by Django 2.1.1 on 2019-08-07 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0007_auto_20190807_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='googleanalyticsview',
            name='ga_account_id',
            field=models.CharField(default='', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='googleanalyticsview',
            name='ga_view_id',
            field=models.CharField(default='', max_length=50, null=True),
        ),
    ]
