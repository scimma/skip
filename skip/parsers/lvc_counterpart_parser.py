from abc import ABC, abstractmethod
from dateutil.parser import parse
import json
import re

from skip.exceptions import ParseError
from skip.models import Alert, Topic
from skip.parsers.base_parser import BaseParser


class LVCCounterpartParser(BaseParser):

    def parse_coordinates(self, alert):
        raw_ra = alert['cntrpart_ra'].split(',')[0]
        raw_dec = alert['cntrpart_dec'].split(',')[0]
        print(raw_ra, raw_dec)
        ra = re.search('^\d+\.\d+', raw_ra).group(0)
        dec = re.search('^\d+\.\d+', raw_dec).group(0)
        print(ra, dec)
        return ra, dec

    def parse_alert(self, alert):
        try:
            role = alert['notice_type']
            target = alert['event_trig_num']
            timestamp = parse(alert['notice_date'])
            print(timestamp)
            ra, dec = self.parse_coordinates(alert)
        except (AttributeError, KeyError, ParseError):
            print('unable to parse lvc-counterpart alert')
            raise ParseError('Unable to parse alert')

        parsed_alert = {
            'target': target,
            'role': role,
            'alert_timestamp': timestamp,
            'alert_identifier': '',
            # 'coordinates': Point(float(ra), float(dec), srid=4035),
            'right_ascension': ra,
            'declination': dec,
            'message': alert
        }

    def save_parsed_alert(self, parsed_alert, topic_name):
        target, created = Topic.objects.get_or_create(name=parsed_alert.pop('target'))
        topic, created = Topic.objects.get_or_create(name=topic_name)
        alert = Alert.objects.create(message=json.dumps(parsed_alert), topic=topic)
        return alert, True
