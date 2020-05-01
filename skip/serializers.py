from skip.models import Event, Target
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['name']


# TODO: ?consider serializers.HyperlinkedModelSerializer??
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['target_id', 'message']
