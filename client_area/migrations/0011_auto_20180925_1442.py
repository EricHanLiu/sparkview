# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-25 14:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0019_auto_20180924_1744'),
        ('budget', '0015_auto_20180925_1326'),
        ('client_area', '0010_auto_20180925_1326'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountChanges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changeField', models.CharField(default='None', max_length=255)),
                ('changedFrom', models.CharField(default='None', max_length=255)),
                ('changedTo', models.CharField(default='None', max_length=255)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_management.Member')),
            ],
        ),
        migrations.RemoveField(
            model_name='clientchanges',
            name='client',
        ),
        migrations.RemoveField(
            model_name='clientchanges',
            name='member',
        ),
        migrations.DeleteModel(
            name='ClientChanges',
        ),
    ]