# Generated by Django 2.1.1 on 2019-08-07 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0006_auto_20190807_0944'),
    ]

    operations = [
        migrations.RenameField(
            model_name='googleanalyticsview',
            old_name='ga_account_view',
            new_name='ga_view_id',
        ),
    ]
