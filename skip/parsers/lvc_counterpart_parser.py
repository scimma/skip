from abc import ABC, abstractmethod
from dateutil.parser import parse
from datetime import datetime, timezone
import json
import re

from django.contrib.gis.geos import Point

from skip.exceptions import ParseError
from skip.models import Alert, Topic
from skip.parsers.base_parser import BaseParser


class LVCCounterpartParser(BaseParser):

    def __repr__(self):
        return 'LVC Counterpart Parser'

    def parse_coordinates(self, alert):
        raw_ra = alert['cntrpart_ra'].split(',')[0]
        raw_dec = alert['cntrpart_dec'].split(',')[0]
        ra = raw_ra.split('d', 1)[0]
        dec = raw_dec.split('d', 1)[0]
        return ra, dec

    def parse_timestamp(self, alert):
        # TODO: the alert contains three different timestamps, we should determine which we want. This method
        # currently returns the event timestamp, rather than the notice or observation timestamps.
        raw_datestamp = alert['obs_date']
        raw_timestamp = alert['obs_time']
        datestamp = re.search(r'\d{2}\/\d{2}\/\d{2}', raw_datestamp)
        parsed_datestamp = parse(datestamp.group(0), yearfirst=True)
        timestamp = re.search(r'\d{2}:\d{2}:\d{2}\.\d{2}', raw_timestamp)
        parsed_timestamp = parse(timestamp.group(0))
        combined_datetime = datetime.combine(parsed_datestamp, parsed_timestamp.time())
        combined_datetime.replace(tzinfo=timezone.utc)
        return combined_datetime

    def parse_alert(self, alert):
        """
        The GNC/LVC Counterpart notices come through as a text blob. The below code parses the lines into key/value
        pairs and adds them to the JSON that will be saved as a message. A couple of notes:

        - RA/Dec are parsed differently because they come through on three lines, each line providing the coordinate
          using a different epoch.
        - An arbitrary number of comment lines are included, each one preceded by 'COMMENT:'.

        At some point we may consider modifying the fields prior to adding them to the parsed alert, and saving the
        raw message as a key/value pair of the `message` field. This could cause complications elsewhere, however.

        The below is a sample message that can be parsed by this method.

        TITLE:            GCN/LVC COUNTERPART NOTICE
        NOTICE_DATE:      Sat 13 Apr 19 02:48:49 UT
        NOTICE_TYPE:      Other 
        CNTRPART_RA:      214.9576d {+14h 19m 49.8s} (J2000),
                          215.1672d {+14h 20m 40.1s} (current),
                          214.4139d {+14h 17m 39.3s} (1950)
        CNTRPART_DEC:     +31.3139d {+31d 18' 50.0"} (J2000),
                          +31.2261d {+31d 13' 33.8"} (current),
                          +31.5428d {+31d 32' 34.1"} (1950)
        CNTRPART_ERROR:   7.2 [arcsec, radius]
        EVENT_TRIG_NUM:   S190412
        EVENT_DATE:       18585 TJD;   102 DOY;   2019/04/12 (yy/mm/dd)
        EVENT_TIME:       19844.00 SOD {05:30:44.00} UT
        OBS_DATE:         18585 TJD;   102 DOY;   19/04/12
        OBS_TIME:         77607.0 SOD {21:33:27.00} UT
        OBS_DUR:          80.2 [sec]
        INTENSITY:        3.50e-12 +/- 1.80e-12 [erg/cm2/sec]
        ENERGY:           0.3-10 [keV]
        TELESCOPE:        Swift-XRT
        SOURSE_SERNUM:    3
        RANK:             4
        WARN_FLAG:        0
        SUBMITTER:        Phil_Evans
        SUN_POSTN:         21.19d {+01h 24m 45s}   +8.90d {+08d 54' 17"}
        SUN_DIST:         137.69 [deg]   Sun_angle= 11.1 [hr] (West of Sun)
        MOON_POSTN:       119.27d {+07h 57m 04s}  +21.28d {+21d 16' 50"}
        MOON_DIST:         83.90 [deg]
        MOON_ILLUM:       54 [%]
        GAL_COORDS:        50.48, 70.30 [deg] galactic lon,lat of the counterpart
        ECL_COORDS:       199.09, 42.19 [deg] ecliptic lon,lat of the counterpart
        COMMENTS:         LVC Counterpart.
        COMMENTS:         This matches a catalogued X-ray source: 1RXS J141947.5+311838
        COMMENTS:         This source has been given a rank of 4
        COMMENTS:         Ranks indicate how likely the object is to be
        COMMENTS:         the GW counterpart. Ranks go from 1-4 with
        COMMENTS:         1 being the most likely and 4 the least.
        COMMENTS:         See http://www.swift.ac.uk/ranks.php for details.
        """
        parsed_alert = {'message': {}}

        try:
            content = alert['content']
            for line in content.splitlines():
                entry = line.split(':', 1)
                if len(entry) > 1:
                    if entry[0] == 'COMMENTS' and 'comments' in parsed_alert['message']:
                        parsed_alert['message']['comments'] += entry[1].lstrip()
                    else:
                        parsed_alert['message'][entry[0].lower()] = entry[1].strip()
                else:
                    # RA is parsed first, so append to RA if dec hasn't been parsed
                    # TODO: modify this to just keep track of the most recent key
                    if 'cntrpart_dec' not in parsed_alert['message']:
                        parsed_alert['message']['cntrpart_ra'] += ' ' + entry[0].strip()
                    else:
                        parsed_alert['message']['cntrpart_dec'] += ' ' + entry[0].strip()

            ra, dec = self.parse_coordinates(parsed_alert['message'])
            parsed_alert['coordinates'] = Point(float(ra), float(dec), srid=4035)

            timestamp = self.parse_timestamp(parsed_alert['message'])
            parsed_alert['alert_timestamp'] = timestamp

            parsed_alert['alert_identifier'] = parsed_alert['message']['event_trig_num']
        except (AttributeError, KeyError, ParseError) as e:
            print(e)
            raise ParseError('Unable to parse alert')

        return parsed_alert

    def save_parsed_alert(self, parsed_alert, topic_name):
        # target, created = Topic.objects.get_or_create(name=parsed_alert.pop('target'))
        topic, created = Topic.objects.get_or_create(name=topic_name)
        parsed_alert['topic'] = topic
        alert = Alert.objects.get_or_create(**parsed_alert)
        return alert, True
