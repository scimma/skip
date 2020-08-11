import json
import time

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from skip.models import Alert


class Command(BaseCommand):

    def handle(self, *args, **options):
        alerts = Alert.objects.filter(message__WhereWhen__ObsDataLocation__ObservationLocation__AstroCoords__Position2D__Name1='RA',
                             message__WhereWhen__ObsDataLocation__ObservationLocation__AstroCoords__Position2D__Name2='Dec', 
                             coordinates=None, topic_id=1)
        for alert in alerts:
            ra  = alert.message['WhereWhen']['ObsDataLocation']['ObservationLocation']['AstroCoords']['Position2D']['Value2']['C1']
            dec = alert.message['WhereWhen']['ObsDataLocation']['ObservationLocation']['AstroCoords']['Position2D']['Value2']['C2']

            coordinates = Point(float(ra), float(dec), srid=4035)

            alert.coordinates = coordinates
            alert.save()
        

        alerts = Alert.objects.filter(message__has_keys=['radeg', 'decdeg'], coordinates=None, topic_id=2)
        for alert in alerts:
            ra  = alert.message['radeg']
            dec = alert.message['decdeg']

            coordinates = Point(float(ra), float(dec), srid=4035)

            alert.coordinates = coordinates
            alert.save()
        