# Generated by Django 2.1.1 on 2019-08-29 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0094_merge_20190827_1420'),
        ('notifications', '0022_auto_20190821_0743'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentEmailRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_type', models.IntegerField(choices=[(0, '95% Spend Warning')], default=0)),
                ('account', models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
            ],
        ),
    ]
