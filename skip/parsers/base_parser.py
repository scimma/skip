from abc import ABC, abstractmethod
import json

from skip.models import Alert, Topic


class BaseParser(ABC):

    @abstractmethod
    def parse_alert(self, alert):
        pass

    @abstractmethod
    def save_parsed_alert(self, parsed_alert, topic_name):
        pass


class DefaultParser(BaseParser):

    def __repr__(self):
        return 'Default Parser'

    def parse_alert(self, alert):
        return alert

    def save_parsed_alert(self, parsed_alert, topic_name):
        print(f'saved {topic_name} alert as default alert')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        alert = Alert.objects.create(message=json.dumps(parsed_alert), topic=topic)
        return True
