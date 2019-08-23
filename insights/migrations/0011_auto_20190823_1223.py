# Generated by Django 2.1.1 on 2019-08-23 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0010_teninsightsreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='teninsightsreport',
            name='aov_per_age_bracket_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='aov_per_medium_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='average_session_duration_per_age_bracket_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='average_session_duration_per_region_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='bounce_rate_per_age_bracket_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='total_goal_completions_per_age_bracket_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='total_goal_completions_per_region_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='total_goal_completions_per_week_day_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='transaction_total_per_product_report',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='teninsightsreport',
            name='transaction_total_per_region_report',
            field=models.TextField(default=''),
        ),
    ]
