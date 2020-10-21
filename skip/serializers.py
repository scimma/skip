from astropy.coordinates import Angle, SkyCoord
from astropy import units

from skip.models import Alert, Target, Topic
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['name', 'right_ascension', 'declination', 'created', 'modified']


class AlertSerializer(serializers.ModelSerializer):
    right_ascension = serializers.SerializerMethodField()
    right_ascension_sexagesimal = serializers.SerializerMethodField()
    declination = serializers.SerializerMethodField()
    declination_sexagesimal = serializers.SerializerMethodField()
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
                  'right_ascension_sexagesimal',
                  'declination_sexagesimal',
                  'role',
                  'extracted_fields',
                  'message',
                  'created',
                  'modified']

    def get_right_ascension(self, obj):
        if obj.coordinates:
            return obj.coordinates.x

    def get_declination(self, obj):
        if obj.coordinates:
            return obj.coordinates.y

    def get_right_ascension_sexagesimal(self, obj):
        if obj.coordinates:
            a = Angle(obj.coordinates.x, unit=units.degree)
            return a.to_string(unit=units.hour, sep=':')

    def get_declination_sexagesimal(self, obj):
        if obj.coordinates:
            a = Angle(obj.coordinates.y, unit=units.degree)
            return a.to_string(unit=units.degree, sep=':')

    def get_topic(self, obj):
        return Topic.objects.get(pk=obj.topic.id).name


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']
