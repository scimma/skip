from skip.models import Event, Target
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['name', 'right_ascension', 'declination', 'created', 'modified']


# TODO: ?consider serializers.HyperlinkedModelSerializer??
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [  # 'target_id',  
                  'event_identifier',
                  'event_timestamp',
                  'right_ascension',
                  'declination',
                  'role',
                  'topic',
                  'message',
                  'created',
                  'modified']
