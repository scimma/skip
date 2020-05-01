import json

from django.conf import settings
from django.core.management.base import BaseCommand

from confluent_kafka import Consumer
from skip.parser import Parser


HOPSKOTCH_SERVER = settings.HOPSKOTCH_SERVER
HOPSKOTCH_PORT = settings.HOPSKOTCH_PORT
HOPSKOTCH_GROUP = settings.HOPSKOTCH_GROUP
HOPSKOTCH_AUTO_OFFSET_RESET = settings.HOPSKOTCH_AUTO_OFFSET_RESET
HOPSKOTCH_TOPICS = settings.HOPSKOTCH_TOPICS
HOPSKOTCH_SECURITY_PROTOCOL = settings.HOPSKOTCH_SECURITY_PROTOCOL
HOPSKOTCH_SASL_MECHANISM = settings.HOPSKOTCH_SASL_MECHANISM
HOPSKOTCH_SASL_USERNAME = settings.HOPSKOTCH_SASL_USERNAME
HOPSKOTCH_SASL_PASSWORD = settings.HOPSKOTCH_SASL_PASSWORD


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        self.consumer = Consumer({
            'bootstrap.servers': f'{HOPSKOTCH_SERVER}:{HOPSKOTCH_PORT}',
            'group.id': HOPSKOTCH_GROUP,
            'auto.offset.reset': HOPSKOTCH_AUTO_OFFSET_RESET,
            'security.protocol': HOPSKOTCH_SECURITY_PROTOCOL,
            'sasl.mechanism': HOPSKOTCH_SASL_MECHANISM,
            'sasl.username': HOPSKOTCH_SASL_USERNAME,
            'sasl.password': HOPSKOTCH_SASL_PASSWORD,            
        })

    def handle(self, *args, **options):

        self.consumer.subscribe(HOPSKOTCH_TOPICS)

        while True:
            print('polling')
            msg = self.consumer.poll(10)
            if msg is None:
                continue
            if msg.error():
                print(msg.error())
                continue
            
            decoded_message = msg.value().decode('utf-8')
            packet = json.loads(decoded_message)
            if packet['role'] != 'utility' and packet['role'] != 'test':
                print(packet)



        self.consumer.close()