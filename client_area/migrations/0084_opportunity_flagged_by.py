# Generated by Django 2.1.1 on 2019-08-13 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0066_member_created'),
        ('client_area', '0083_auto_20190812_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='flagged_by',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_management.Member'),
        ),
    ]