parsers = {
    'gcn': ['GCNParser', 'BaseParser']
}


class BaseParser():

    def parse_and_save_alert(alert):
        pass


class DefaultParser(BaseParser):

    def parse_and_save_alert(alert):
        event = Event.objects.create(message=json.dumps(alert))
        return event


class GCNParser(BaseParser):
    
    def parse_and_save_alert(alert):
        try:
            coordinates = 
