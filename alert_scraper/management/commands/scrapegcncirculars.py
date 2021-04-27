import re
import requests
import sys

from bs4 import BeautifulSoup
from dateutil.parser import parse, parserinfo
from django.core.management.base import BaseCommand
from gracedb_sdk import Client

from alert_scraper.models import ScrapedAlert


class Command(BaseCommand):
    """
    Produces 1572 alerts.
    """
    superevent_regex = re.compile(r'S\d{6}[a-z]+')
    gcn_archive_urls = [
        'selected.html',
        'selected_2019.html'
    ]

    def __init__(self, *args, **kwargs):
        gracedb_client = Client()
        self.superevent_ids = [se['superevent_id'] for se in gracedb_client.superevents.search(query='category: Production')]

    def handle(self, *args, **options):
        for superevent_id in self.superevent_ids:
            print(superevent_id)
            response = requests.get(f'https://gcn.gsfc.nasa.gov/other/{superevent_id}.gcn3')
            circulars = re.split(r'\/{10,}', response.text)
            for circular in circulars:
                for line in circular.splitlines():
                    entry = line.split(':', 1)
                    if len(entry) > 1:
                        if entry[0] == 'DATE':
                            ScrapedAlert.objects.get_or_create(
                                alert=circular,
                                timestamp=parse(entry[1], parserinfo=parserinfo(yearfirst=True)),
                                alert_type='lvc_circular'
                            )
                            break
