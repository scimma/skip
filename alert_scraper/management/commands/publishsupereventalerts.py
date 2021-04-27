from django.conf import settings
from django.core.management.base import BaseCommand
from hop import Stream
from hop.auth import Auth
from hop.models import GCNCircular

from alert_scraper.models import ScrapedAlert


class Command(BaseCommand):

    # topic_mapping = {
    #     'lvc_notice': 'gcn',
    #     'lvc_counterpart': 'lvc.lvc-counterpart',
    #     'lvc_circular': 'gcn-circular'
    # }

    def handle(self, *args, **options):
        scraped_alerts = ScrapedAlert.objects.all().order_by('timestamp')
        stream = Stream(auth=Auth(settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.username'],
                                  settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.password']))

        with stream.open('kafka://dev.hop.scimma.org:9092/lvc.gcn-circular-test', 'w') as s:
            for alert in scraped_alerts:
                if alert.alert_type == 'lvc_circular':
                    circular = GCNCircular.load(alert.alert)
                    s.write(circular)
                # else:
                #     s.write(alert.alert)
