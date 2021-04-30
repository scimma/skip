from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from confluent_kafka import Message
from django.core.management import call_command
from django.test import override_settings, TestCase

from skip.management.commands.ingestmessages import Command
from skip.models import Alert, Event, Topic
from skip.parsers.gcn_circular_parser import GCNCircularParser


test_superevent_circular_message = {
    'format': 'circular',
    'content': {
        'header': {
            'TITLE': 'GCN CIRCULAR',
            'NUMBER': '24442',
            'SUBJECT': 'LIGO/Virgo S190510g: Identification of a GW compact binary merger candidate',
            'DATE': '19/05/10 05:51:38 GMT',
            'FROM': 'Eric Howell at Aus.Intl.Grav.Res.Centre/UWA  <eric.howell@uwa.edu.au>'
        },
        'body': 'The LIGO Scientific Collaboration and the Virgo Collaboration report: \n\ntest content'
    }
}


class TestGCNCircularParser(TestCase):
    def setUp(self):
        topic = Topic.objects.create(name='gcn-circular')
        self.alert = Alert.objects.create(message=test_superevent_circular_message, topic=topic)

    def test_parse(self):
        parser = GCNCircularParser()
        parsed = parser.parse(self.alert)
        
        self.assertTrue(parsed)
        self.assertDictContainsSubset({'title': 'GCN CIRCULAR', 'number': '24442'}, self.alert.message)
        self.assertEqual(datetime(2019, 5, 10, 5, 51, 38, tzinfo=timezone.utc), self.alert.alert_timestamp)
        self.assertEqual('24442', self.alert.alert_identifier)
        event = self.alert.events.first()
        self.assertTrue(event.event_identifier=='S190510g')


@override_settings(HOPSKOTCH_PARSERS={'gcn-circular': 'skip.parsers.gcn_circular_parser.GCNCircularParser'})
class TestGCNCircularIngestion(TestCase):
    def setUp(self):
        pass

    @patch('skip.management.commands.ingestmessages.Consumer')
    def test_ingest(self, mock_consumer):
        mock_message = MagicMock()
        mock_message.configure_mock(**{
            'topic.return_value': 'gcn-circular',
            'value.return_value': test_superevent_circular_message,
            'error.return_value': None
        })
        # mock_message.topic.return_value = 'gcn-circular'
        # mock_message.value.return_value = test_superevent_circular_message
        # mock_message.error.return_value = None
        print(mock_message.error())
        print(mock_message.value())
        mock_consumer.poll.return_value = mock_message
        print(mock_consumer.poll().error())
        print(mock_consumer.poll().value())
        # mock_consumer = MockConsumer()
        # print(mock_consumer.poll(1).error())

        call_command('ingestmessages')
        # command = Command()
        # command.handle()
