# Generated by Django 2.1.1 on 2018-11-14 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='account',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='budget.Client'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='confirmed_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='link',
            field=models.URLField(blank=True, max_length=499),
        ),
        migrations.AlterField(
            model_name='notification',
            name='member',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='user_management.Member'),
        ),
    ]