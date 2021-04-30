import re
import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.core.management.base import BaseCommand
from hop import Stream
from hop.auth import Auth

from alert_scraper.models import ScrapedAlert


class Command(BaseCommand):
    """
    Note: this produces 234 alerts, but there are 240 VO Events in GraceDB.
    """
    notice_link_regex = re.compile(r'notices_l/S\d{6}[a-z]+\.lvc')
    slash_regex = re.compile(r'\/+')

    def handle(self, *args, **options):
        response = requests.get('https://gcn.gsfc.nasa.gov/lvc_events.html')
        soup = BeautifulSoup(response.content)
        table = soup.find('table')
        rows = table.find_all('tr')
        for row in rows:
            for cell in row.find_all('td'):
                a = cell.find('a')
                if a and self.notice_link_regex.findall(a['href']):
                    notices_response = requests.get(f"https://gcn.gsfc.nasa.gov/{a['href']}")
                    notices = re.split(r'\/{10,}', notices_response.text)
                    for notice in notices:
                        for line in notice.splitlines():
                            entry = line.split(':', 1)
                            if len(entry) > 1:
                                if entry[0] == 'NOTICE_DATE':
                                    ScrapedAlert.objects.get_or_create(alert=notice, timestamp=parse(entry[1]), alert_type='lvc_notice')
