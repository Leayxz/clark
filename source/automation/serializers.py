from rest_framework import serializers

class ConfigurationSerializer(serializers.Serializer):
    marginUSD = serializers.IntegerField()
    leverage = serializers.IntegerField()
    buy_variation = serializers.DecimalField(max_digits=5, decimal_places=0)
    percentage_profit = serializers.DecimalField(max_digits=5, decimal_places=2)


class ExchangeSerializer(serializers.Serializer):
    exchange = serializers.CharField(max_length=15)


class AutomationAPISerializer(serializers.Serializer):
    API_KEY = serializers.CharField(max_length=50)
    API_SECRET = serializers.CharField(max_length=90)
    API_PASSPHRASE = serializers.CharField(max_length=10)
    exchange = serializers.CharField(max_length=15)
