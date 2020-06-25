from skip.models import Alert, Target, Topic
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['name', 'right_ascension', 'declination', 'created', 'modified']


# TOOD: use field exclusion instead of inclusion:
#   see https://www.django-rest-framework.org/api-guide/serializers/#specifying-which-fields-to-include
# TODO: ?consider serializers.HyperlinkedModelSerializer??
class AlertSerializer(serializers.ModelSerializer):
    # location = serializers.SerializerMethodField()
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

    # def get_location(self, obj):
    #     if not obj.coordinates:
    #         return
    #     return (obj.coordinates.x, obj.coordinates.y)

    def get_target(self, obj):
        return Target.objects.get(pk=obj.target.id).name

    def get_topic(self, obj):
        return Topic.objects.get(pk=obj.topic.id).name


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']
