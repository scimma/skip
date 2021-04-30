from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from confluent_kafka import Message
from django.core.management import call_command
from django.test import override_settings, TestCase

from skip.management.commands.ingestmessages import Command
from skip.models import Alert, Event, Topic
from skip.parsers.gcn_lvc_notice_plaintext_parser import GCNLVCNoticeParser


test_superevent_notice = {
    'format': 'blob',
    'content': 
        'TITLE:            GCN/LVC NOTICE\n'
        'NOTICE_DATE:      Mon 16 Mar 20 22:01:09 UT\n'
        'NOTICE_TYPE:      LVC Preliminary\n'
        'TRIGGER_NUM:      S200316bj\n'
        'TRIGGER_DATE:     18924 TJD;    76 DOY;   2020/03/16 (yyyy/mm/dd)\n'
        'TRIGGER_TIME:     79076.157221 SOD {21:57:56.157221} UT\n'
        'SEQUENCE_NUM:     1\n'
        'GROUP_TYPE:       1 = CBC\n'
        'SEARCH_TYPE:      1 = AllSky\n'
        'PIPELINE_TYPE:    4 = gstlal\n'
        'FAR:              7.099e-11 [Hz]  (one per 163037.0 days)  (one per 446.68 years)\n'
        'PROB_NS:          0.00 [range is 0.0-1.0]\n'
        'PROB_REMNANT:     0.00 [range is 0.0-1.0]\n'
        'PROB_BNS:         0.00 [range is 0.0-1.0]\n'
        'PROB_NSBH:        0.00 [range is 0.0-1.0]\n'
        'PROB_BBH:         0.00 [range is 0.0-1.0]\n'
        'PROB_MassGap:     0.99 [range is 0.0-1.0]\n'
        'PROB_TERRES:      0.00 [range is 0.0-1.0]\n'
        'TRIGGER_ID:       0x10\n'
        'MISC:             0x1898807\n'
        'SKYMAP_FITS_URL:  https://gracedb.ligo.org/api/superevents/S200316bj/files/bayestar.fits.gz,0\n'
        'EVENTPAGE_URL:    https://gracedb.ligo.org/superevents/S200316bj/view/\n'
        'COMMENTS:         LVC Preliminary Trigger Alert.  \n'
        'COMMENTS:         This event is an OpenAlert.  \n'
        'COMMENTS:         LIGO-Hanford Observatory contributed to this candidate event.  \n'
        'COMMENTS:         LIGO-Livingston Observatory contributed to this candidate event.  \n'
        'COMMENTS:         VIRGO Observatory contributed to this candidate event.\n'
}


class TestGCNLVCNoticeParser(TestCase):
    def setUp(self):
        topic = Topic.objects.create(name='gcn')
        self.alert = Alert.objects.create(message=test_superevent_notice, topic=topic)

    # TODO: mock out get_confidence_regions
    # @patch('skip.parsers.gcn_lvc_notice_plaintext_parser.get_confidence_regions')
    def test_parse(self):
        parser = GCNLVCNoticeParser()
        parsed = parser.parse(self.alert)
        
        self.assertTrue(parsed)
        self.assertDictContainsSubset({'title': 'GCN/LVC NOTICE', 'trigger_num': 'S200316bj'}, self.alert.message)
        self.assertEqual(datetime(2020, 3, 16, 22, 1, 9, tzinfo=timezone.utc), self.alert.alert_timestamp)
        self.assertEqual('S200316bj', self.alert.alert_identifier)

        event = self.alert.events.first()
        self.assertTrue(event.event_identifier=='S200316bj')
        event_attributes = event.eventattributes_set.first()
        self.assertDictContainsSubset(
            {'far': '7.099e-11', 'prob_ns': '0.00', 'prob_remnant': '0.00', 'prob_bns': '0.00', 'prob_nsbh': '0.00',
             'prob_bbh': '0.00', 'prob_massgap': '0.99', 'prob_terres': '0.00'},
            event_attributes.attributes
        )
        self.assertEqual(1, event_attributes.sequence_number)
        self.assertEqual('LVC Preliminary', event_attributes.tag)
