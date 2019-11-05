# Generated by Django 2.1.1 on 2019-10-24 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0097_merge_20191016_0843'),
        ('user_management', '0085_auto_20191015_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountMemberHourHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.IntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)),
                ('year', models.PositiveSmallIntegerField(blank=True, default=1999)),
                ('actual_hours', models.FloatField(default=0.0)),
                ('allocated_hours', models.FloatField(default=0.0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='budget.Client')),
                ('member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_management.Member')),
            ],
        ),
    ]