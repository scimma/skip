from skip.exceptions import ParseError
from skip.models import Event
from skip.parsers.base_parser import BaseParser


class GCNParser(BaseParser):

    def parse_coordinates(self, alert):
        # A Position2D JSON object comes through like so:
        #   "Position2D":{
        #     "unit":"deg",
        #     "Name1":"RA",
        #     "Name2":"Dec",
        #     "Value2":{
        #        "C1":"285.4246",
        #        "C2":"5.1321"
        #     },
        #     "Error2Radius":"0.0000"
        #   }   
        # 
        # Though the VOEvent specification implies that RA will always be in the `C1` field and Dec will always 
        # be in the `C2` field, it offers no guarantee of this. However, we are making the assumption that it is 
        # consistent.
        coordinates = {}

        try:
            coordinates = alert['WhereWhen']['ObsDataLocation']['ObservationLocation']['AstroCoords']['Position2D']
            ra = coordinates['Value2']['C1']
            dec = coordinates['Value2']['C2']
            return ra, dec
        except AttributeError:
            raise Exception('Unable to parse coordinates')


    def parse_alert(self, alert, topic):
        successful_parsing = False

        try:
            role = alert['role']
            event_identifier = alert['ivorn']
            ra, dec = self.parse_coordinates(alert)
            # successful_parsing = True
        except AttributeError:
            raise ParseError()

        parsed_alert = {
            'role': role,
            'event_identifier': event_identifier,
            'topic': topic,
            'right_ascension': ra,
            'declination': dec,
            'message': alert
        }

        return parsed_alert
        # return parsed_alert, successful_parsing
        

    def save_parsed_alert(self, parsed_alert):
        print(parsed_alert)
        # print(**parsed_alert)
        event, created = Event.objects.get_or_create(**parsed_alert)
        return created
