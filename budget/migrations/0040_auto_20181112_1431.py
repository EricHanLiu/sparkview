# Generated by Django 2.1.1 on 2018-11-12 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0039_budgetupdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountbudgetspendhistory',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='budget.Client'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='adwords',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AlterField(
            model_name='budgetupdate',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='budget.Client'),
        ),
        migrations.AlterField(
            model_name='campaigngrouping',
            name='adwords',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AlterField(
            model_name='campaigngrouping',
            name='bing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bing_dashboard.BingAccounts'),
        ),
        migrations.AlterField(
            model_name='campaigngrouping',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='budget.Client'),
        ),
        migrations.AlterField(
            model_name='campaigngrouping',
            name='facebook',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='facebook_dashboard.FacebookAccount'),
        ),
        migrations.AlterField(
            model_name='client',
            name='clientType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='client_type', to='client_area.ClientType'),
        ),
        migrations.AlterField(
            model_name='client',
            name='industry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='industry', to='client_area.Industry'),
        ),
        migrations.AlterField(
            model_name='client',
            name='managementFee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='client_area.ManagementFeesStructure'),
        ),
        migrations.AlterField(
            model_name='client',
            name='parentClient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='client_area.ParentClient'),
        ),
        migrations.AlterField(
            model_name='client',
            name='soldBy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sold_by', to='user_management.Member'),
        ),
        migrations.AlterField(
            model_name='clientcdata',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='budget.Client'),
        ),
        migrations.AlterField(
            model_name='flightbudget',
            name='adwords_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='adwords_dashboard.DependentAccount'),
        ),
        migrations.AlterField(
            model_name='flightbudget',
            name='bing_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bing_dashboard.BingAccounts'),
        ),
        migrations.AlterField(
            model_name='flightbudget',
            name='facebook_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='facebook_dashboard.FacebookAccount'),
        ),
    ]