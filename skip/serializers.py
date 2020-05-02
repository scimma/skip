from skip.models import Event, Target
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['name']


# TOOD: use field exclusion instead of inclusion:
#   see https://www.django-rest-framework.org/api-guide/serializers/#specifying-which-fields-to-include
# TODO: ?consider serializers.HyperlinkedModelSerializer??
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['target_id', 'message']
