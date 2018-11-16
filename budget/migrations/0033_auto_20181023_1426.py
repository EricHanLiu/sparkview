# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-23 14:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0032_remove_client_projection_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='am1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='am1', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='am2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='am2', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='am3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='am3', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='amb',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='amb', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='cm1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cm1', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='cm2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cm2', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='cm3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cm3', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='cmb',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cmb', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='seo1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seo1', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='seo2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seo2', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='seo3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seo3', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='seob',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seob', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='strat1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='strat1', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='strat2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='strat2', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='strat3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='strat3', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='client',
            name='stratb',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stratb', to='user_management.Member'),
        ),
    ]