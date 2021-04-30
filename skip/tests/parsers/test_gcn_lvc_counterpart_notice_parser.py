from datetime import datetime, timezone

from django.test import TestCase

from skip.models import Alert, Event, Topic
from skip.parsers.gcn_lvc_counterpart_notice_parser import GCNLVCCounterpartNoticeParser


test_superevent_counterpart_notice = {
    'format': 'blob',
    'content':
        'TITLE:            GCN/LVC COUNTERPART NOTICE\n'
        'NOTICE_DATE:      Fri 26 Apr 19 23:13:39 UT\n'
        'NOTICE_TYPE:      Other \n'
        'CNTRPART_RA:      299.8851d {+19h 59m 32.4s} (J2000),\n'
        '                  300.0523d {+20h 00m 12.5s} (current),\n'
        '                  299.4524d {+19h 57m 48.5s} (1950)\n'
        'CNTRPART_DEC:     +40.7310d {+40d 43\' 51.6"} (J2000),\n'
        '                  +40.7847d {+40d 47\' 04.9"} (current),\n'
        '                  +40.5932d {+40d 35\' 35.4"} (1950)\n'
        'CNTRPART_ERROR:   7.6 [arcsec, radius]\n'
        'EVENT_TRIG_NUM:   S190426\n'
        'EVENT_DATE:       18599 TJD;   116 DOY;   2019/04/26 (yy/mm/dd)\n'
        'EVENT_TIME:       55315.00 SOD {15:21:55.00} UT\n'
        'OBS_DATE:         18599 TJD;   116 DOY;   19/04/26\n'
        'OBS_TIME:         73448.0 SOD {20:24:08.00} UT\n'
        'OBS_DUR:          72.7 [sec]\n'
        'INTENSITY:        1.00e-11 +/- 2.00e-12 [erg/cm2/sec]\n'
        'ENERGY:           0.3-10 [keV]\n'
        'TELESCOPE:        Swift-XRT\n'
        'SOURSE_SERNUM:    2\n'
        'RANK:             2\n'
        'WARN_FLAG:        0\n'
        'SUBMITTER:        Phil_Evans\n'
        'SUN_POSTN:         34.11d {+02h 16m 26s}  +13.66d {+13d 39\' 45"}\n'
        'SUN_DIST:          84.13 [deg]   Sun_angle= 6.3 [hr] (West of Sun)\n'
        'MOON_POSTN:       309.58d {+20h 38m 19s}  -19.92d {-19d 55\' 00"}\n'
        'MOON_DIST:         61.34 [deg]\n'
        'MOON_ILLUM:       50 [%]\n'
        'GAL_COORDS:        76.19,  5.74 [deg] galactic lon,lat of the counterpart\n'
        'ECL_COORDS:       317.73, 59.32 [deg] ecliptic lon,lat of the counterpart\n'
        'COMMENTS:         LVC Counterpart.  \n'
        'COMMENTS:         This matches a catalogued X-ray source: 1RXH J195932.6+404351  \n'
        'COMMENTS:         This source has been given a rank of 2  \n'
        'COMMENTS:         Ranks indicate how likely the object is to be  \n'
        'COMMENTS:         the GW counterpart. Ranks go from 1-4 with   \n'
        'COMMENTS:         1 being the most likely and 4 the least.  \n'
        'COMMENTS:         See http://www.swift.ac.uk/ranks.php for details.  \n'
        'COMMENTS:         MAY match a known transient, will be checked manually.\n'
}


class TestGCNLVCCounterpartNoticeParser(TestCase):
    def setUp(self):
        topic = Topic.objects.create(name='lvc.lvc-counterpart')
        self.alert = Alert.objects.create(raw_message=test_superevent_counterpart_notice, topic=topic)
        self.event = Event.objects.create(identifier='S190426c')

    def test_parse(self):
        parser = GCNLVCCounterpartNoticeParser(self.alert)
        parsed = parser.parse()

        self.assertTrue(parsed)
        self.assertDictContainsSubset({'title': 'GCN/LVC COUNTERPART NOTICE', 'event_trig_num': 'S190426'},
                                      self.alert.parsed_message)
        self.assertEqual(datetime(2019, 4, 26, 20, 24, 8, tzinfo=timezone.utc), self.alert.timestamp)
        self.assertEqual('S190426_X2', self.alert.identifier)
        self.assertEqual(299.8851, self.alert.coordinates.coords[0])
        self.assertEqual(40.7310, self.alert.coordinates.coords[1])

        event = self.alert.events.first()
        self.assertTrue(event.identifier == 'S190426c')
        self.assertEqual(Event.objects.count(), 1)
