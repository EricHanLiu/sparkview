from rest_framework import serializers
from . import models


class AccountSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.DependentAccount
        fields = ('dependent_account_id', 'dependent_account_name')
        # fields = '__all__'

class PerformanceSerializer(serializers.HyperlinkedModelSerializer):
    account = AccountSerializer(many=False, read_only=True)

    class Meta:
        model = models.Performance
        fields = ('account', 'performance_type', 'cpc', 'clicks', 'conversions',
        'cost', 'cost_per_conversions', 'ctr', 'impressions',
        'search_impr_share')
