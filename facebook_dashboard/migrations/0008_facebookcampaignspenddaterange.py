# Generated by Django 2.1.1 on 2019-06-20 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_dashboard', '0007_facebookcampaign_master_exclusion'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookCampaignSpendDateRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spend', models.FloatField(default=0.0)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('campaign', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='facebook_dashboard.FacebookCampaign')),
            ],
        ),
    ]