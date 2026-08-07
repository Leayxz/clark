from rest_framework import serializers

class InputTelegramSerializer(serializers.Serializer):
    telegram_id = serializers.CharField(max_length=5)
    telegram_token = serializers.CharField(max_length=5)
