from django.conf import settings
from django.core.management.base import BaseCommand
from hop import Stream
from hop.auth import Auth
from hop.models import GCNCircular

from alert_scraper.models import ScrapedAlert


class Command(BaseCommand):

    topic_mapping = {
        'lvc_counterpart': 'lvc.lvc-counterpart',
        'lvc_notice': 'gcn',
        'lvc_circular': 'gcn-circular'
    }

    def handle(self, *args, **options):
        for alert_type, topic in self.topic_mapping.items():
            stream = Stream(auth=Auth(settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.username'],
                                      settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.password']))
            with stream.open(f'kafka://dev.hop.scimma.org:9092/{topic}', 'w') as s:
                scraped_alerts = ScrapedAlert.objects.filter(alert_type=alert_type).order_by('timestamp')
                for alert in scraped_alerts:
                    if alert.alert_type == 'lvc_circular':
                        try:
                            circular = GCNCircular.load(alert.alert_data.read().decode('utf-8'))
                            s.write(circular)
                        except:
                            pass
                    else:
                        s.write(alert.alert)
