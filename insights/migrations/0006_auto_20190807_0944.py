# Generated by Django 2.1.1 on 2019-08-07 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0005_auto_20190807_0942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='googleanalyticsreport',
            name='report',
        ),
        migrations.AddField(
            model_name='googleanalyticsreport',
            name='dimensions',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
