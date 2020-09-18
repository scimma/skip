from copy import deepcopy
import json

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F
from rest_framework.renderers import JSONRenderer
from skip_dpd.skip_client import SkipClient

from skip.filters import AlertFilter, TopicFilter
from skip.models import Alert, Topic
from skip.serializers import AlertSerializer, TopicSerializer

SKIP_BASE_URL = 'http://skip.dev.hop.scimma.org/api'
SKIP_API_KEY = settings.SKIP_API_KEY


class SkipORMClient(SkipClient):

    def get_alerts(self, *args, **kwargs):
        page_num = kwargs.pop('page', 1)
        page_size = kwargs.pop('page_size', 20)
        print(kwargs)
        af = AlertFilter(kwargs, queryset=Alert.objects.all().order_by(F('alert_timestamp').desc(nulls_last=True)))
        print(af.__dir__())
        paginator = Paginator(af.qs, page_size)
        alerts = AlertSerializer(paginator.page(page_num).object_list, many=True)

        # TODO: find a way to return as dict for performance rather than needing to do json.loads()
        # TODO: or figure out why OrderedDict doesn't work with Dash
        return json.loads(JSONRenderer().render(alerts.data))

    def get_topics(self, *args, **kwargs):
        tf = TopicFilter(kwargs, queryset=Topic.objects.all())
        topics = TopicSerializer(tf.qs, many=True)

        return json.loads(JSONRenderer().render(topics.data))
