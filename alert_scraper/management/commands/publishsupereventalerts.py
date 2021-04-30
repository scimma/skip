from django.conf import settings
from django.core.management.base import BaseCommand
from hop import Stream
from hop.auth import Auth
from hop.models import GCNCircular

from alert_scraper.models import ScrapedAlert


class Command(BaseCommand):

    # topic_mapping = {
    #     'lvc_notice': 'gcn-test',
    #     'lvc_counterpart': 'lvc.lvc-counterpart-test',
    #     'lvc_circular': 'gcn-circular-test'
    # }

    def handle(self, *args, **options):
        scraped_alerts = ScrapedAlert.objects.all().order_by('timestamp')
        stream = Stream(auth=Auth(settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.username'],
                                  settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.password']))

        with stream.open('kafka://dev.hop.scimma.org:9092/lvc.gcn-test', 'w') as s:
            for alert in scraped_alerts:
                if alert.alert_type == 'lvc_circular':
                    try:
                        circular = GCNCircular.load(alert.alert_data.read().decode('utf-8'))
                        s.write(circular)
                    except:
                        pass
                else:
                    s.write(alert.alert)
