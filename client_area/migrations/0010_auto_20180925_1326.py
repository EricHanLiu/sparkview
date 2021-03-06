# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-25 13:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0019_auto_20180924_1744'),
        ('budget', '0015_auto_20180925_1326'),
        ('client_area', '0009_accounthourrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientChanges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changeField', models.CharField(default='None', max_length=255)),
                ('changedFrom', models.CharField(default='None', max_length=255)),
                ('changedTo', models.CharField(default='None', max_length=255)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_management.Member')),
            ],
        ),
        migrations.AddField(
            model_name='parentclient',
            name='name',
            field=models.CharField(default='No name', max_length=255),
        ),
    ]
