from importlib import import_module
import json
import logging
import time

from confluent_kafka import Consumer
from django.conf import settings
from django.core.management.base import BaseCommand

from skip.exceptions import ParseError

logger = logging.getLogger(__name__)

HOPSKOTCH_CONSUMER_CONFIGURATION = settings.HOPSKOTCH_CONSUMER_CONFIGURATION
HOPSKOTCH_TOPICS = settings.HOPSKOTCH_TOPICS
PARSERS = settings.HOPSKOTCH_PARSERS
POLLING_INTERVAL = settings.POLLING_INTERVAL


def get_parser_classes(topic):
    parser_classes = []

    for parser in PARSERS.get(topic, []) + PARSERS.get('default', []):
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
        super().__init__(*args, **kwargs)
        self.consumer = Consumer(HOPSKOTCH_CONSUMER_CONFIGURATION)

    def handle(self, *args, **options):
        self.consumer.subscribe(HOPSKOTCH_TOPICS)
        roles = {}

        while True:
            logger.log(msg=f'Polling topics {HOPSKOTCH_TOPICS} every {POLLING_INTERVAL} seconds', level=logging.INFO)
            msg = self.consumer.poll(POLLING_INTERVAL)
            if msg is None:
                continue
            if msg.error():
                logger.log(msg=f'Error consuming message: {msg.error()}', level=logging.WARN)
                continue

            # TODO: message handling should be moved into method
            topic = msg.topic()
            
            decoded_message = msg.value().decode('utf-8')
            packet = json.loads(decoded_message)

            # For whatever reason, TNS packets needs to be serialized to JSON twice. This should probably be handled
            # elsewhere/differently
            if topic == 'tns':
                packet = json.loads(packet)

            logger.log(msg=f'Processing alert: {packet}', level=logging.INFO)

            parser_classes = get_parser_classes(topic)
            for parser_class in parser_classes:
                alert_content = packet['content']
                parser = parser_class()
                saved_alert = parser.save_alert(alert_content, topic)

                if saved_alert:
                    logger.log(msg=f'saved alert {saved_alert}', level=logging.INFO)
                    break

        self.consumer.close()
