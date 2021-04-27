import re
import requests
from bs4 import BeautifulSoup

from dateutil.parser import parse
from django.core.management.base import BaseCommand

from alert_scraper.models import ScrapedAlert


class Command(BaseCommand):
    """
    Note: this produces 203 alerts, but Ron's script produced 382.
    """
    counterpart_link_regex = re.compile(r'other/S\d{6}[a-z]+\.counterpart')

    def handle(self, *args, **options):
        response = requests.get('https://gcn.gsfc.nasa.gov/counterpart_tbl.html')
        soup = BeautifulSoup(response.content)
        table = soup.find('table')
        rows = table.find_all('tr')
        for row in rows:
            for cell in row.find_all('td'):
                a = cell.find('a')
                if a and self.counterpart_link_regex.findall(a['href']):
                    notices_response = requests.get(f"https://gcn.gsfc.nasa.gov/{a['href']}")
                    notices = re.split(r'\/{10,}', notices_response.text)
                    for notice in notices:
                        for line in notice.splitlines():
                            entry = line.split(':', 1)
                            if len(entry) > 1:
                                if entry[0] == 'NOTICE_DATE':
                                    ScrapedAlert.objects.get_or_create(alert=notice, timestamp=parse(entry[1]), alert_type='lvc_counterpart')
