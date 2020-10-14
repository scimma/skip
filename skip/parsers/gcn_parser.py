import logging
from dateutil.parser import parse

from django.contrib.gis.geos import Point

from skip.exceptions import ParseError
from skip.models import Alert, Topic
from skip.parsers.base_parser import BaseParser


logger = logging.getLogger(__name__)


class GCNParser(BaseParser):

    def __repr__(self):
        return 'GCN Parser'

    def parse_coordinates(self, alert):
        # A Position2D JSON object comes through like so:
        #   "Position2D":{
        #     "unit":"deg",
        #     "Name1":"RA",
        #     "Name2":"Dec",
        #     "Value2":{
        #        "C1":"285.4246",
        #        "C2":"5.1321"
        #     },
        #     "Error2Radius":"0.0000"
        #   }   
        # 
        # Though the VOEvent specification implies that RA will always be in the `C1` field and Dec will always 
        # be in the `C2` field, it offers no guarantee of this. However, we are making the assumption that it is 
        # consistent.
        coordinates = {}

        try:
            coordinates = alert['WhereWhen']['ObsDataLocation']['ObservationLocation']['AstroCoords']['Position2D']
            ra = coordinates['Value2']['C1']
            dec = coordinates['Value2']['C2']
            return ra, dec
        except (AttributeError, KeyError):
            # TODO: Alerts of role `utility` appear to have a different format--should be explored further rather than 
            # shunted off to the DefaultParser
            raise ParseError('Unable to parse coordinates')


    def parse_alert(self, alert):
        alert = alert['content']

        try:
            role = alert['role']
            alert_identifier = alert['ivorn']
            alert_timestamp = parse(alert['Who']['Date'])
            ra, dec = self.parse_coordinates(alert)
        except (AttributeError, KeyError, ParseError) as e:
            logger.log(msg=f'Unable to parse GCN alert: {e}', level=logging.WARN)
            # TODO: How do we want to handle cascading exceptions?
            raise ParseError('Unable to parse alert')

        parsed_alert = {
            'role': role,
            'alert_timestamp': alert_timestamp,
            'alert_identifier': alert_identifier,
            'coordinates': Point(float(ra), float(dec), srid=4035),
            'message': alert
        }

        return parsed_alert

    def save_parsed_alert(self, parsed_alert, topic_name):
        topic, created = Topic.objects.get_or_create(name=topic_name)
        parsed_alert['topic'] = topic
        alert, created = Alert.objects.get_or_create(**parsed_alert)
        return created
