from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class FundWalletSerializer(serializers.Serializer):
    wallet_to = serializers.CharField(max_length=42)

class AnalyticsSerializer(serializers.Serializer):
    successful_transactions = serializers.IntegerField()
    failed_transactions= serializers.IntegerField()