# Generated by Django 2.1.1 on 2019-08-27 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0073_auto_20190822_1001'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='backupperiod',
            options={'ordering': ['-start_date']},
        ),
    ]
