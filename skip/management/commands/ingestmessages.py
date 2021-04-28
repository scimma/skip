from importlib import import_module
import json
import logging
import time

from confluent_kafka import Consumer
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from skip.models import Alert, Topic
from skip.parsers.base_parser import DefaultParser

logger = logging.getLogger(__name__)

HOPSKOTCH_CONSUMER_CONFIGURATION = settings.HOPSKOTCH_CONSUMER_CONFIGURATION
HOPSKOTCH_TOPICS = settings.HOPSKOTCH_TOPICS
HOPSKOTCH_CONSUMER_POLLING_TIMEOUT = settings.HOPSKOTCH_CONSUMER_POLLING_TIMEOUT
HOPSKOTCH_PARSERS = settings.HOPSKOTCH_PARSERS


def get_parser_class(topic):
    """
    return the parser class for the given topic.
    If there is no entry in the settings.HOPSKOTCH_PARSERS dictionary for this topic,
    the return the 'default' parser class.
    """
    try:
        parser = HOPSKOTCH_PARSERS[topic]
    except KeyError:
        parser = HOPSKOTCH_PARSERS['default']
        logger.log(msg=f'HOPSKOTCH_PARSER not found for topic: {topic}. Using default parser.', level=logging.WARNING)

    module_name, class_name = parser.rsplit('.', 1)

    # TODO: the seems like an overly complicated way to get the parser class imported
    #  is there precedent for this method?
    try:
        module = import_module(module_name)
        parser_class = getattr(module, class_name)
    except (ImportError, AttributeError):
        raise ImportError(f'Unable to import parser {parser}')

    return parser_class


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.consumer = Consumer(HOPSKOTCH_CONSUMER_CONFIGURATION)

    def handle(self, *args, **options):
        self.consumer.subscribe(HOPSKOTCH_TOPICS)

        while True:
            logger.log(msg=f'Polling topics {HOPSKOTCH_TOPICS} with timeout of {HOPSKOTCH_CONSUMER_POLLING_TIMEOUT} seconds', level=logging.INFO)
            # msg = self.consumer.poll(HOPSKOTCH_CONSUMER_POLLING_TIMEOUT)
            msg = self.consumer.consume(num_messages=1)  # TODO: remove
            msg = msg[0]  # TODO: remove
            if msg is None:
                continue
            if msg.error():
                logger.warn(msg=f'Error consuming message: {msg.error()}')
                continue

            topic_name = msg.topic()
            topic, _ = Topic.objects.get_or_create(name=topic_name)

            decoded_message = msg.value().decode('utf-8')
            packet = json.loads(decoded_message)

            # For whatever reason, TNS packets needs to be serialized to JSON twice. This should probably be handled
            # elsewhere/differently
            if topic.name == 'tns':
                packet = json.loads(packet)

            logger.log(msg=f'Processing alert: {packet}', level=logging.INFO)

            alert = Alert.objects.create(topic=topic, message=packet)

            with transaction.atomic():
                # Get the parser class, instantiate it, parse the alert, and save it
                parser_class = get_parser_class(topic.name)
                parser = parser_class()
                alert.parsed = parser.parse(alert)
                alert.save()

            if alert.parsed is True:
                logger.info(msg=f'saved alert {alert}')
                time.sleep(1)
            else:
                logger.warn(msg=f'Unable to parse alert {alert}: {packet}')
                time.sleep(1)


        self.consumer.close()
