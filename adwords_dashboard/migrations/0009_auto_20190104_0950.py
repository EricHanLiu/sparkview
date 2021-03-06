# Generated by Django 2.1.1 on 2019-01-04 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adwords_dashboard', '0008_auto_20181112_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adgroup',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AlterField(
            model_name='adgroup',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adwords_dashboard.Campaign'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AlterField(
            model_name='dependentaccount',
            name='assigned_am',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aw_am', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dependentaccount',
            name='assigned_cm2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aw_cm2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dependentaccount',
            name='assigned_cm3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aw_cm3', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dependentaccount',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='label',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AlterField(
            model_name='performance',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adwords_dashboard.DependentAccount'),
        ),
    ]
