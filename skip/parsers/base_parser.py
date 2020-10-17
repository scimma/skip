from abc import ABC, abstractmethod
import json
import logging

from skip.models import Alert, Topic


logger = logging.getLogger(__name__)


class BaseParser(ABC):

    @abstractmethod
    def parse_alert(self, alert):
        pass

    def save_alert(self, alert_content, topic_name):
        parsed_alert = self.parse_alert(alert_content)

        if parsed_alert:
            topic, created = Topic.objects.get_or_create(name=topic_name)
            alert = Alert.objects.create(**parsed_alert, topic=topic)
            logger.log(msg=f'Saved alert from topic {topic_name} with parser {self}.', level=logging.INFO)
            return alert
        else:
            return

class DefaultParser(BaseParser):

    def __repr__(self):
        return 'Default Parser'

    def parse_alert(self, alert):
        return {'message': alert}
