# Generated by Django 2.1.1 on 2019-03-15 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0036_remove_backup_similar'),
        ('budget', '0059_client_budget_updated'),
        ('client_area', '0052_auto_20190307_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpsellAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.IntegerField(choices=[(1, 'PPC'), (2, 'SEO'), (3, 'CRO')], default=1)),
                ('result', models.IntegerField(choices=[(1, 'Pending'), (2, 'Unsuccessful'), (3, 'Success')], default=1)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='budget.Client')),
                ('attempted_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_management.Member')),
            ],
        ),
    ]
