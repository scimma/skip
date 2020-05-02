import json

from django.conf import settings
from django.core.management.base import BaseCommand

from confluent_kafka import Consumer


HOPSKOTCH_CONSUMER_CONFIGURATION = settings.HOPSKOTCH_CONSUMER_CONFIGURATION
HOPSKOTCH_TOPICS = settings.HOPSKOTCH_TOPICS


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        print(HOPSKOTCH_CONSUMER_CONFIGURATION)
        self.consumer = Consumer(HOPSKOTCH_CONSUMER_CONFIGURATION)

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