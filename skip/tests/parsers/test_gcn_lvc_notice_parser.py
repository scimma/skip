from datetime import datetime, timezone
from unittest.mock import patch

from django.test import TestCase

from skip.models import Alert, Topic
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
        self.alert = Alert.objects.create(raw_message=test_superevent_notice, topic=topic)

    @patch('skip.parsers.gcn_lvc_notice_plaintext_parser.GCNLVCNoticeParser.get_confidence_regions')
    def test_parse(self, mock_get_regions):
        mock_get_regions.return_value = (1, 2)
        parser = GCNLVCNoticeParser(self.alert)
        parsed = parser.parse()

        self.assertTrue(parsed)
        self.assertDictContainsSubset({'title': 'GCN/LVC NOTICE', 'trigger_num': 'S200316bj'},
                                      self.alert.parsed_message)
        self.assertEqual(datetime(2020, 3, 16, 22, 1, 9, tzinfo=timezone.utc), self.alert.timestamp)
        self.assertEqual('S200316bj', self.alert.identifier)

        event = self.alert.events.first()
        self.assertTrue(event.identifier == 'S200316bj')
        event_attributes = event.eventattributes_set.first()
        self.assertDictContainsSubset(
            {'far': '7.099e-11', 'prob_ns': '0.00', 'prob_remnant': '0.00', 'prob_bns': '0.00', 'prob_nsbh': '0.00',
             'prob_bbh': '0.00', 'prob_massgap': '0.99', 'prob_terres': '0.00'},
            event_attributes.attributes
        )
        self.assertEqual(1, event_attributes.sequence_number)
        self.assertEqual('LVC Preliminary', event_attributes.tag)
