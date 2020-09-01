from dateutil.parser import parse

from django.contrib.gis.geos import Point

from skip.exceptions import ParseError
from skip.models import Alert, Topic
from skip.parsers.base_parser import BaseParser


class TNSParser(BaseParser):

    def __repr__(self):
        return 'TNS Parser'

    def parse_coordinates(self, alert):
        # The TNS message contains sexagesimal RA/Dec in fields 'ra' and 'dec', and degree values in fields 'radeg'
        # and 'decdeg'.
        try:
            ra = alert['radeg']
            dec = alert['decdeg']
            return ra, dec
        except (AttributeError, KeyError):
            # TODO: Alerts of role `utility` appear to have a different format--should be explored further rather than 
            # shunted off to the DefaultParser
            raise ParseError('Unable to parse coordinates')

    def parse_alert(self, alert):

        try:
            alert = alert['content']
            print(alert)
            alert_identifier = alert['name_prefix'] + alert['objname']
            alert_timestamp = parse(alert['discoverydate'])
            ra, dec = self.parse_coordinates(alert)
        except (AttributeError, KeyError, ParseError) as e:
            print(e)
            # TODO: How do we want to handle cascading exceptions?
            raise ParseError('Unable to parse alert')

        parsed_alert = {
            'role': None,
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
