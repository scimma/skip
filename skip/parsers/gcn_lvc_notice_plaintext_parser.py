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

    def __repr__(self):
        return 'GCN/LVC Notice Parser'

    def associate_event(self):
        events = Event.objects.filter(event_identifier__icontains=self.alert.alert_identifier)
        event = events.first() if events.exists() else Event.objects.create(event_identifier=self.alert.alert_identifier)
        event.alert_set.add(self.alert)
        event.save()
        return event

    def populate_event_attributes(self, event):
        attributes = {k: self.alert.message.get(k, '').split(' ', 1)[0] for k in ['far', 'prob_ns', 'prob_remnant',
                                                                                  'prob_bns', 'prob_nsbh', 'prob_bbh',
                                                                                  'prob_massgap', 'prob_terres']}
        area_50, area_90 = self.get_confidence_regions('skymap_fits_url')
        attributes['area_50'] = area_50 if area_50 else ''
        attributes['area_90'] = area_90 if area_90 else ''

        EventAttributes.objects.create(
            event=event,
            attributes=attributes,
            tag=self.alert.message['notice_type'],
            sequence_number=self.alert.message['sequence_num']
        )

    def is_alert_parsable(self):
        return all(x.lower() in self.alert.message['title'].lower() for x in ['GCN', 'LVC', 'NOTICE'])

    def parse_message(self):
        alert_message = self.alert.message['content']
        self.alert.message = {}  # we don't want the unparsed message stored alongside the parsed keys
        try:
            for line in alert_message.splitlines():
                entry = line.split(':', 1)
                if len(entry) > 1:
                    if entry[0] == 'COMMENTS' and 'comments' in self.alert.message:
                        self.alert.message['comments'] += entry[1].lstrip()
                    else:
                        self.alert.message[entry[0].lower()] = entry[1].strip()
        except Exception as e:
            logger.warn(f'parse_message failed for {self.alert}: {e}')
            self.alert.message = {'content': alert_message}  # restore the original message if parsing fails

    def parse_notice_date(self):
        self.alert.alert_timestamp = parse(self.alert.message['notice_date'], tzinfos={'UT': timezone.utc})

    def parse_trigger_number(self):
        self.alert.alert_identifier = self.alert.message['trigger_num']

    def parse(self):
        try:
            self.parse_message()

            if not self.is_alert_parsable():
                return False

            self.parse_trigger_number()

            event = self.associate_event()
            self.populate_event_attributes(event)            
            
            self.parse_notice_date()
        except Exception as e:
            logger.warn(f'Unable to parse alert {self.alert} with parser {self}: {e}')
            return False
        
        return True
