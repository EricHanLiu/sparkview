# Generated by Django 2.1.1 on 2019-03-06 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0034_backup_similar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backup',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_by', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='backup',
            name='similar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='similar_member', to='user_management.Member'),
        ),
    ]