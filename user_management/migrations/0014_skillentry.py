# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-12 12:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0013_auto_20180911_1930'),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='user_management.Member')),
                ('skill', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='user_management.Skill')),
            ],
        ),
    ]
