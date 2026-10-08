from rest_framework import serializers

class GoalSerializer(serializers.Serializer):
    goal_target = serializers.IntegerField(min_value=1)
