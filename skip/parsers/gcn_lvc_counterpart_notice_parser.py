from dateutil.parser import parse
from datetime import datetime, timezone
from gzip import decompress
import io
import logging
import re
import requests

from astropy.io import fits
from django.contrib.gis.geos import Point
from django.core.cache import cache
from gracedb_sdk import Client
import healpy as hp
import numpy as np
import voeventparse as vp

from skip.exceptions import ParseError
from skip.models import Alert
from skip.parsers.base_parser import BaseParser


logger = logging.getLogger(__name__)


class GCNLVCCounterpartNoticeParser(BaseParser):
    """
    Sample GCN/LVC Counterpart Notice:

    TITLE:            GCN/LVC COUNTERPART NOTICE
    NOTICE_DATE:      Fri 26 Apr 19 23:13:39 UT
    NOTICE_TYPE:      Other 
    CNTRPART_RA:      299.8851d {+19h 59m 32.4s} (J2000),
                      300.0523d {+20h 00m 12.5s} (current),
                      299.4524d {+19h 57m 48.5s} (1950)
    CNTRPART_DEC:     +40.7310d {+40d 43' 51.6"} (J2000),
                      +40.7847d {+40d 47' 04.9"} (current),
                      +40.5932d {+40d 35' 35.4"} (1950)
    CNTRPART_ERROR:   7.6 [arcsec, radius]
    EVENT_TRIG_NUM:   S190426
    EVENT_DATE:       18599 TJD;   116 DOY;   2019/04/26 (yy/mm/dd)
    EVENT_TIME:       55315.00 SOD {15:21:55.00} UT
    OBS_DATE:         18599 TJD;   116 DOY;   19/04/26
    OBS_TIME:         73448.0 SOD {20:24:08.00} UT
    OBS_DUR:          72.7 [sec]
    INTENSITY:        1.00e-11 +/- 2.00e-12 [erg/cm2/sec]
    ENERGY:           0.3-10 [keV]
    TELESCOPE:        Swift-XRT
    SOURSE_SERNUM:    2
    RANK:             2
    WARN_FLAG:        0
    SUBMITTER:        Phil_Evans
    SUN_POSTN:         34.11d {+02h 16m 26s}  +13.66d {+13d 39' 45"}
    SUN_DIST:          84.13 [deg]   Sun_angle= 6.3 [hr] (West of Sun)
    MOON_POSTN:       309.58d {+20h 38m 19s}  -19.92d {-19d 55' 00"}
    MOON_DIST:         61.34 [deg]
    MOON_ILLUM:       50 [%]
    GAL_COORDS:        76.19,  5.74 [deg] galactic lon,lat of the counterpart
    ECL_COORDS:       317.73, 59.32 [deg] ecliptic lon,lat of the counterpart
    COMMENTS:         LVC Counterpart.  
    COMMENTS:         This matches a catalogued X-ray source: 1RXH J195932.6+404351  
    COMMENTS:         This source has been given a rank of 2  
    COMMENTS:         Ranks indicate how likely the object is to be  
    COMMENTS:         the GW counterpart. Ranks go from 1-4 with   
    COMMENTS:         1 being the most likely and 4 the least.  
    COMMENTS:         See http://www.swift.ac.uk/ranks.php for details.  
    COMMENTS:         MAY match a known transient, will be checked manually.
    """

    def __repr__(self):
        return 'GCN/LVC Counterpart Notice Parser'

    @staticmethod
    def associate_event(alert):
        event = Event.objects.get_or_create(event_identifier__icontains=alert.message['event_trig_num'])
        event.alert_set.add(alert)
        event.save()
        return event

    @staticmethod
    def is_gcn_lvc_counterpart_notice(alert):
        return all(x.lower() in alert.message['title'].lower() for x in ['GCN', 'LVC', 'COUNTERPART', 'NOTICE'])

    def parse_event_trig_num(self, alert):
        """
        Sources are of the format S123456_X1, that is, event trigger number + '_X' + source serial number
        """
        event_trigger_number = alert.message['event_trig_num']
        source_sernum = alert.message['sourse_sernum']
        alert.alert_identifier = f'{event_trigger_number}_X{source_sernum}'

    def parse_coordinates(self, alert):
        raw_ra = alert['cntrpart_ra'].split(',')[0]
        raw_dec = alert['cntrpart_dec'].split(',')[0]
        alert.right_ascension = raw_ra.split('d', 1)[0]
        alert.declination = raw_dec.split('d', 1)[0]

    def parse_message(self, alert):
        print('parse message')
        alert_message = alert.message['content']
        alert.message = {}
        try:
            for line in alert_message.splitlines():
                entry = line.split(':', 1)
                if len(entry) > 1:
                    if entry[0] == 'COMMENTS' and 'comments' in alert.message:
                        alert.message['comments'] += entry[1].lstrip()
                    else:
                        alert.message[entry[0].lower()] = entry[1].strip()
                else:
                    # RA is parsed first, so append to RA if dec hasn't been parsed
                    # TODO: modify this to just keep track of the most recent key
                    if 'cntrpart_dec' not in alert.message:
                        alert.message['cntrpart_ra'] += ' ' + entry[0].strip()
                    else:
                        alert.message['cntrpart_dec'] += ' ' + entry[0].strip()
        except Exception as e:
            logger.warn(f'parse_message failed for {alert}: {e}')
            alert.message = alert_message

    def parse_obs_timestamp(self, alert):
        # TODO: the alert contains three different timestamps, we should determine which we want. This method
        # currently returns the observation timestamp, rather than the notice or event timestamps.
        raw_datestamp = alert.message['obs_date']
        raw_timestamp = alert.message['obs_time']
        datestamp = re.search(r'\d{2}\/\d{2}\/\d{2}', raw_datestamp)
        parsed_datestamp = parse(datestamp.group(0), yearfirst=True)
        timestamp = re.search(r'\d{2}:\d{2}:\d{2}\.\d{2}', raw_timestamp)
        parsed_timestamp = parse(timestamp.group(0))
        combined_datetime = datetime.combine(parsed_datestamp, parsed_timestamp.time())
        combined_datetime.replace(tzinfo=timezone.utc)
        alert.alert_timestamp = combined_datetime

    def parse(self, alert):
        try:
            self.parse_message(alert)
            print('parsed_message')

            if not GCNLVCCounterpartNoticeParser.is_gcn_lvc_counterpart_notice(alert):
                print('False')
                return False

            GCNLVCCounterpartNoticeParser.associate_event(alert)

            self.parse_obs_timestamp(alert)
            print('parsed timestamp')

            self.parse_coordinates(alert)
            print('parsed coordinates')
        except Exception as e:
            logger.warn(f'Unable to parse alert {alert} with parser {self}: {e}')
            return False

        return True
