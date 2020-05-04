from importlib import import_module
import json

from confluent_kafka import Consumer
from django.conf import settings
from django.core.management.base import BaseCommand

from skip.exceptions import ParseError


HOPSKOTCH_CONSUMER_CONFIGURATION = settings.HOPSKOTCH_CONSUMER_CONFIGURATION
HOPSKOTCH_TOPICS = settings.HOPSKOTCH_TOPICS
PARSERS = settings.PARSERS


def get_parser_classes(topic):
    parser_classes = []

    for parser in PARSERS.get(topic, []):
        module_name, class_name = parser.rsplit('.', 1)
        try:
            module = import_module(module_name)
            parser_class = getattr(module, class_name)
        except (ImportError, AttributeError):
            raise ImportError(f'Unable to import parser {parser}')
        parser_classes.append(parser_class)
    
    return parser_classes


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        print(HOPSKOTCH_CONSUMER_CONFIGURATION)
        self.consumer = Consumer(HOPSKOTCH_CONSUMER_CONFIGURATION)

    def handle(self, *args, **options):

        self.consumer.subscribe(HOPSKOTCH_TOPICS)
        roles = {}

        while True:
            print('polling')
            msg = self.consumer.poll(10)
            if msg is None:
                continue
            if msg.error():
                print(msg.error())
                continue
            
            topic = msg.topic()
            decoded_message = msg.value().decode('utf-8')
            packet = json.loads(decoded_message)

            parser_classes = get_parser_classes(topic)
            for parser_class in parser_classes:
                saved = False
                try:
                    parser = parser_class()
                    parsed_alert = parser.parse_alert(packet, topic)
                    saved = parser.save_parsed_alert(parsed_alert)
                except ParseError:
                    continue
                print(saved)
                if saved:
                    break


        self.consumer.close()