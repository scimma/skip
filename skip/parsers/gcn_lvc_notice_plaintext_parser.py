import logging
from datetime import timezone

from dateutil.parser import parse
from django.contrib.gis.geos import Point

from skip.exceptions import ParseError
from skip.models import Alert, Event, EventAttributes, Topic
from skip.parsers.base_parser import BaseParser


logger = logging.getLogger(__name__)


class GCNLVCNoticeParser(BaseParser):
    """
    Sample GCN/LVC Notice:

    TITLE:            GCN/LVC NOTICE
    NOTICE_DATE:      Mon 16 Mar 20 22:01:09 UT
    NOTICE_TYPE:      LVC Preliminary
    TRIGGER_NUM:      S200316bj
    TRIGGER_DATE:     18924 TJD;    76 DOY;   2020/03/16 (yyyy/mm/dd)
    TRIGGER_TIME:     79076.157221 SOD {21:57:56.157221} UT
    SEQUENCE_NUM:     1
    GROUP_TYPE:       1 = CBC
    SEARCH_TYPE:      1 = AllSky
    PIPELINE_TYPE:    4 = gstlal
    FAR:              7.099e-11 [Hz]  (one per 163037.0 days)  (one per 446.68 years)
    PROB_NS:          0.00 [range is 0.0-1.0]
    PROB_REMNANT:     0.00 [range is 0.0-1.0]
    PROB_BNS:         0.00 [range is 0.0-1.0]
    PROB_NSBH:        0.00 [range is 0.0-1.0]
    PROB_BBH:         0.00 [range is 0.0-1.0]
    PROB_MassGap:     0.99 [range is 0.0-1.0]
    PROB_TERRES:      0.00 [range is 0.0-1.0]
    TRIGGER_ID:       0x10
    MISC:             0x1898807
    SKYMAP_FITS_URL:  https://gracedb.ligo.org/api/superevents/S200316bj/files/bayestar.fits.gz,0
    EVENTPAGE_URL:    https://gracedb.ligo.org/superevents/S200316bj/view/
    COMMENTS:         LVC Preliminary Trigger Alert.  
    COMMENTS:         This event is an OpenAlert.  
    COMMENTS:         LIGO-Hanford Observatory contributed to this candidate event.  
    COMMENTS:         LIGO-Livingston Observatory contributed to this candidate event.  
    COMMENTS:         VIRGO Observatory contributed to this candidate event.
    """
    # alert = None
    # event = None

    # def __init__(self, alert, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.alert = alert

    def __repr__(self):
        return 'GCN/LVC Notice Parser'

    @staticmethod
    def associate_event(alert):
        events = Event.objects.filter(event_identifier__icontains=alert.alert_identifier)
        event = events.first() if events.exists() else Event.objects.create(event_identifier=alert.alert_identifier)
        event.alert_set.add(alert)
        event.save()
        return event

    @staticmethod
    def populate_event_attributes(alert, event):
        attributes = {k: alert.message.get(k, '').split(' ', 1)[0] for k in ['far', 'prob_ns', 'prob_remnant', 'prob_bns',
                                                                         'prob_nsbh', 'prob_bbh', 'prob_massgap',
                                                                         'prob_terres']}
        area_50, area_90 = GCNLVCNoticeParser.get_confidence_regions(alert.message.get('skymap_fits_url', ''))
        print(area_50)
        attributes['area_50'] = area_50 if area_50 else ''
        attributes['area_90'] = area_90 if area_90 else ''

        EventAttributes.objects.create(
            event=event,
            attributes=attributes,
            tag=alert.message['notice_type'],
            sequence_number=alert.message['sequence_num']
        )

    @staticmethod
    def is_gcn_lvc_notice(alert):
        print(alert.message)
        return all(x.lower() in alert.message['title'].lower() for x in ['GCN', 'LVC', 'NOTICE'])

    def parse_message(self, alert):
        alert_message = alert.message['content']
        alert.message = {}  # we don't want the unparsed message stored alongside the parsed keys
        try:
            for line in alert_message.splitlines():
                entry = line.split(':', 1)
                if len(entry) > 1:
                    if entry[0] == 'COMMENTS' and 'comments' in alert.message:
                        alert.message['comments'] += entry[1].lstrip()
                    else:
                        alert.message[entry[0].lower()] = entry[1].strip()
        except Exception as e:
            logger.warn(f'parse_message failed for {alert}: {e}')
            alert.message = {'content': alert_message}  # restore the original message if parsing fails

    def parse_notice_date(self, alert):
        alert.alert_timestamp = parse(alert.message['notice_date'], tzinfos={'UT': timezone.utc})

    def parse_trigger_number(self, alert):
        alert.alert_identifier = alert.message['trigger_num']

    def parse(self, alert):
        try:
            self.parse_message(alert)

            if not GCNLVCNoticeParser.is_gcn_lvc_notice(alert):
                return False

            self.parse_trigger_number(alert)

            event = GCNLVCNoticeParser.associate_event(alert)
            GCNLVCNoticeParser.populate_event_attributes(alert, event)            
            
            self.parse_notice_date(alert)
        except Exception as e:
            logger.warn(f'Unable to parse alert {alert} with parser {self}: {e}')
            return False
        
        return True
