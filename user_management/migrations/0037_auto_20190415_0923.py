# Generated by Django 2.1.1 on 2019-04-15 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0036_remove_backup_similar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incident',
            name='additional_comments',
        ),
        migrations.RemoveField(
            model_name='incident',
            name='refund_amount',
        ),
        migrations.RemoveField(
            model_name='incident',
            name='refund_required',
        ),
        migrations.AddField(
            model_name='incident',
            name='budget_error_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='incident',
            name='email',
            field=models.CharField(default='', max_length=355),
        ),
        migrations.AddField(
            model_name='incident',
            name='issue_type',
            field=models.IntegerField(choices=[(0, 'Budget Error'), (1, 'Promotion Error'), (2, 'Text Ad Error'), (3, 'Lack of Activity Error'), (4, 'Communication Error'), (5, 'Other')], default=0),
        ),
        migrations.AddField(
            model_name='incident',
            name='service',
            field=models.IntegerField(choices=[(0, 'Paid Media'), (1, 'SEO'), (2, 'CRO'), (3, 'Client Services'), (4, 'Biz Dev'), (5, 'Internal Oops')], default=0),
        ),
        migrations.AlterField(
            model_name='incident',
            name='platform',
            field=models.IntegerField(choices=[(0, 'Adwords'), (1, 'Facebook'), (2, 'Bing'), (3, 'Other')], default=0),
        ),
    ]
