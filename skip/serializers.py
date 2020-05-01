from skip_api.models import Event, Target
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target


class EventSerializer(serializers.EventSerializer):
    class Meta:
        model = Event
