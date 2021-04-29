import io
import re
import requests
import sys

from bs4 import BeautifulSoup
from dateutil.parser import parse, parserinfo
from django.core import files
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
            response = requests.get(f'https://gcn.gsfc.nasa.gov/other/{superevent_id}.gcn3')
            circulars = re.split(r'\/{10,}', response.text)
            for circular in circulars:
                date = None
                file_name = None
                file_content = io.BytesIO()
                for line in circular.splitlines():
                    entry = line.split(':', 1)
                    if len(entry) > 1:
                        if entry[0] == 'NUMBER':
                            alert_id = entry[1].strip()
                            response = requests.get(f'https://gcn.gsfc.nasa.gov/gcn3/{alert_id}.gcn3', stream=True)
                            file_content.write(response.content)
                            file_name = f'{alert_id}.gcn3'
                        elif entry[0] == 'DATE' and 'MAG:' not in entry[1]:
                            date = parse(entry[1], parserinfo=parserinfo(yearfirst=True))
                if date and file_name and file_content:
                    alert = ScrapedAlert.objects.create(
                        alert_type='lvc_circular',
                        timestamp=date,
                    )
                    alert.alert_data.save(file_name, files.File(file_content))
                    alert.save()
