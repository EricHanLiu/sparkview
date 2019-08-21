# Generated by Django 2.1.1 on 2019-08-16 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0091_auto_20190815_1403'),
        ('insights', '0009_insight'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenInsightsReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField(default=0)),
                ('year', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='budget.Client')),
                ('ga_view', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='insights.GoogleAnalyticsView')),
            ],
        ),
    ]