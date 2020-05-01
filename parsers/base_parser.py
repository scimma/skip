from abc import ABC, abstractmethod


class BaseParser(ABC):

    @abstractmethod
    def parse_alert(alert):
        pass

    @abstractmethod
    def save_parsed_alert(parsed_alert):
        pass
