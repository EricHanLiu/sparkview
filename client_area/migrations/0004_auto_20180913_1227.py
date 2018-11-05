# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-13 12:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0008_remove_clientchanges_datetime'),
        ('user_management', '0016_auto_20180913_1227'),
        ('client_area', '0003_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberClientRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
                ('member', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='user_management.Member')),
            ],
        ),
        migrations.CreateModel(
            name='MemberClientRelationshipType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='name',
            field=models.CharField(default='No name', max_length=255),
        ),
        migrations.AddField(
            model_name='memberclientrelationship',
            name='relationship',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='client_area.MemberClientRelationshipType'),
        ),
        migrations.AlterUniqueTogether(
            name='memberclientrelationship',
            unique_together=set([('relationship', 'client')]),
        ),
    ]
