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
    location = serializers.SerializerMethodField()
    # topic = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = [  # 'target_id',  
                  'alert_identifier',
                  'alert_timestamp',
                #   'topic',
                  'location',
                  'role',
                  'message',
                  'created',
                  'modified']

    def get_location(self, obj):
        return (obj.coordinates.x, obj.coordinates.y)

    # def get_topic(self, obj):
    #     return Topic.objects.first(pk=obj.topic_id)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['name']
