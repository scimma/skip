import base64
import io
import json

from confluent_kafka import Consumer


def start_ingest():
    consumer = Consumer({
        'bootstrap.servers': 'dev.hop.scimma.org:9092',
        'group.id': 'skip-test-1',
        'auto.offset.reset': 'earliest',
        'security.protocol': 'sasl_ssl',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'test',
        'sasl.password': '',
    })
    consumer.subscribe(['gcn'])

    while True:
        print('polling')
        msg = consumer.poll(10)
        if msg is None:
            continue
        if msg.error():
            print(msg.error())
            continue
    
        decoded_message = msg.value().decode('utf-8')
        packet = json.loads(decoded_message)


    consumer.close()


if __name__ == '__main__':
    start_ingest()
