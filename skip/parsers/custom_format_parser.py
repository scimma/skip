from datetime import datetime
from dateutil.parser import parse, parserinfo
import logging

from django.contrib.gis.geos import Point

from skip.parsers.base_parser import BaseParser


logger = logging.getLogger(__name__)


class CustomFormatParser(BaseParser):
    """
    Sample alert:

    {
        "date": "2021-09-22",
        "time": "10:12"
        "title":"Test Alert",
        "author":"David Collom",
        "author_email":"dcollom@lco.global",
        "right_ascension":"340",
        "declination":"-20"
    }
    """

    def __repr__(self):
        return 'Custom Format Parser'

    def parse_coordinates(self):
        ra = self.alert.raw_message['content']['right_ascension']
        dec = self.alert.raw_message['content']['declination']
        self.alert.coordinates = Point(float(ra), float(dec), srid=4035)

    def parse_date(self):
        date_value = parse(self.alert.raw_message['content']['date'], parserinfo=parserinfo(yearfirst=True))
        time_value = parse(self.alert.raw_message['content']['time'], parserinfo=parserinfo(yearfirst=True))
        self.alert.timestamp = datetime.combine(date_value, time_value.time())

    def parse_message(self):
        alert_message = self.alert.raw_message['content']
        try:
            for key, value in alert_message.items():
                self.alert.parsed_message[key.lower()] = value
        except Exception as e:
            logger.warn(f'parse_message failed for {self.alert}: {e}')

    def parse_number(self):
        self.alert.identifier = self.alert.parsed_message['number']

    def parse(self):
        try:
            self.parse_coordinates()

            self.parse_date()

            self.parse_message()

        except Exception as e:
            logger.warn(f'Unable to parse alert {self.alert} with parser {self}: {e}')
            return False

        return True
