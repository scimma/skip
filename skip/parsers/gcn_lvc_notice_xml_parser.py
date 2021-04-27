import logging
from dateutil.parser import parse

from django.contrib.gis.geos import Point

from skip.exceptions import ParseError
from skip.models import Alert, Topic
from skip.parsers.base_parser import BaseParser


logger = logging.getLogger(__name__)


class GCNLVCNoticeParser(BaseParser):

    def __repr__(self):
        return 'GCN/LVC Notice Parser'

    def parse_coordinates(self, alert):
        coordinates = {}

        return coordinates

    def parse(self, alert):
        parsed_alert = {}

        parsed_alert['message'] = alert

        return parsed_alert
