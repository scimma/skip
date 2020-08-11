from skip.models import Alert, Target, Topic
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['name', 'right_ascension', 'declination', 'created', 'modified']


class AlertSerializer(serializers.ModelSerializer):
    right_ascension = serializers.SerializerMethodField()
    declination = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = [ 
                #   'target',
                  'id',
                  'alert_identifier',
                  'alert_timestamp',
                  'topic',
                  'right_ascension',
                  'declination',
                  'role',
                  'message',
                  'created',
                  'modified']

    def get_right_ascension(self, obj):
        if obj.coordinates:
            return obj.coordinates.x

    def get_declination(self, obj):
        if obj.coordinates:
            return obj.coordinates.y

    def get_topic(self, obj):
        return Topic.objects.get(pk=obj.topic.id).name


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']
