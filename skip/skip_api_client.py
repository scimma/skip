from copy import deepcopy
import json

from django.conf import settings
from django.core.paginator import Paginator
from rest_framework.renderers import JSONRenderer
from skip_dpd.skip_api_client import SkipAPIClient

from skip.filters import AlertFilter
from skip.models import Alert
from skip.serializers import AlertSerializer

SKIP_BASE_URL = 'http://skip.dev.hop.scimma.org/api'
SKIP_API_KEY = settings.SKIP_API_KEY


class SkipORMClient(SkipAPIClient):

    def get_alerts(self, *args, **kwargs):
        page = kwargs.pop('page', 1)
        page_size = kwargs.pop('page_size', 20)
        af = AlertFilter(kwargs, queryset=Alert.objects.all())
        paginator = Paginator(af.qs, page_size)
        alerts = AlertSerializer(paginator.page(page).object_list, many=True)

        # TODO: find a way to return as dict for performance rather than needing to do json.loads()
        return json.loads(JSONRenderer().render(alerts.data))
