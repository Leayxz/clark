from rest_framework import serializers

class GoalSerializer(serializers.Serializer):
    goal_target = serializers.IntegerField(min_value=1)


class PeriodSerializer(serializers.Serializer):
    period = serializers.ChoiceField(choices=["today", "month", "all_time"])
