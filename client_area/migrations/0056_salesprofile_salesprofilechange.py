# Generated by Django 2.1.1 on 2019-03-19 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0059_client_budget_updated'),
        ('client_area', '0055_auto_20190315_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ppc_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('seo_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('cro_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('strat_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('feed_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('email_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('account', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
            ],
        ),
        migrations.CreateModel(
            name='SalesProfileChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.IntegerField(choices=[(0, 'ppc'), (1, 'seo'), (2, 'cro'), (3, 'strat'), (4, 'feed'), (5, 'email')], default=0)),
                ('from_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('to_status', models.IntegerField(choices=[(0, 'onboarding'), (1, 'active'), (2, 'inactive'), (3, 'lost'), (4, 'opportunity'), (5, 'pitched')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='client_area.SalesProfile')),
            ],
        ),
    ]