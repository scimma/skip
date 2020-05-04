from skip.models import Alert, Target
from rest_framework import serializers


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['name', 'right_ascension', 'declination', 'created', 'modified']


# TOOD: use field exclusion instead of inclusion:
#   see https://www.django-rest-framework.org/api-guide/serializers/#specifying-which-fields-to-include
# TODO: ?consider serializers.HyperlinkedModelSerializer??
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [  # 'target_id',  
                  'alert_identifier',
                  'alert_timestamp',
                  'right_ascension',
                  'declination',
                  'role',
                  'message',
                  'created',
                  'modified']
