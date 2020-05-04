from abc import ABC, abstractmethod


class BaseParser(ABC):

    @abstractmethod
    def parse_alert(self, alert, topic):
        pass

    @abstractmethod
    def save_parsed_alert(self, parsed_alert):
        pass


class DefaultParser(BaseParser):

    def parse_alert(self, alert, topic):
        return alert

    def save_parsed_alert(self, parsed_alert):
        event = Event.objects.create(message=json.dumps(parsed_alert))
        return event, True
