import math

from django.db.models import Q
from django_filters import rest_framework as filters
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.contrib.gis.measure import D

from skip.models import Topic


EARTH_RADIUS_METERS = 6371008.77141506


class TopicFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_topic_name', label='Topic Search', help_text='Search for topic name')

    def filter_topic_name(self, queryset, name, value):
        return queryset.filter(name=value)


class AlertFilter(filters.FilterSet):
    keyword = filters.CharFilter(method='filter_keyword_search', label='Keyword Search', help_text='Text Search')
    cone_search = filters.CharFilter(method='filter_cone_search', label='Cone Search', 
                                     help_text='RA, Dec, Radius (degrees)')
    polygon_search = filters.CharFilter(method='filter_polygon_search', label='Polygon Search',
                                        help_text='Comma-separated pairs of space-delimited coordinates (degrees).')
    alert_timestamp = filters.DateTimeFromToRangeFilter()
    role = filters.ChoiceFilter(choices=(('utility', 'Utility'), ('test', 'Test'), ('observation', 'Observation')),
                                null_label='None')
    topic = filters.ModelMultipleChoiceFilter(queryset=Topic.objects.all())
    event_trigger_number = filters.CharFilter(method='filter_event_trigger_number', label='LVC Trigger Number')
    ordering = filters.OrderingFilter(
        fields=(
            ('alert_timestamp', 'alert_timestamp')
        )
    )

    def filter_event_trigger_number(self, queryset, name, value):
        print('filtering on event trigger number')
        print(value)
        print(queryset.filter(topic__name='lvc-counterpart', message__event_trig_num__icontains=value).count())
        return queryset.filter(topic__name='lvc-counterpart', message__event_trig_num__icontains=value)

    def filter_cone_search(self, queryset, name, value):
        ra, dec, radius = value.split(',')

        ra = float(ra)
        dec = float(dec)

        radius_meters = 2 * math.pi * EARTH_RADIUS_METERS * float(radius) / 360

        return queryset.filter(coordinates__distance_lte=(Point(ra, dec), D(m=radius_meters)))

    def filter_polygon_search(self, queryset, name, value):
        # TODO: document this function in a docstring with example value input and resulting vertices
        value += ', ' + value.split(', ', 1)[0]
        vertices = tuple((float(v.split(' ')[0]), float(v.split(' ')[1])) for v in value.split(', '))  # TODO: explain this!
        polygon = Polygon(vertices, srid=4035)
        return queryset.filter(coordinates__within=polygon)

    def filter_keyword_search(self, queryset, name, value):
        """
        Look for every value keyword in every keypath field.
        Assumes value is a comma-separated list of keywords to search for.

        This method constructs a django.db.models.Q object for every keyword X keypath
        and OR's them together to pass to Alerts.objects.filter(). The Q-object becomes
        the WHERE-clause of the SQL query that filters the queryset.

        NB: At the moment there are no special indexes created.
        """
        # create list of keywords from comma-separated string. remove leading/trailing white-space.
        query_keywords = [keyword.strip() for keyword in value.split(',')]

        # TODO: move keypaths to settings.py
        # TODO: Discuss keypath list with Andy
        # TODO: if performance becomes an issue, collect keypath string-values into index-able internal field

        # keypaths defines the list of fields that will be searched for the keywords.
        # a keypath is a list of dictionary keys that drill into nested alert dictionaries.
        keypaths = [
            # GCN keypaths
            ['message', 'How', 'Description'],
            ['message', 'Who', 'Author', 'shortName'],
            ['message', 'Who', 'Author', 'contactName'],
            ['message', 'Who', 'Author', 'contactEmail'],
            ['message', 'Why', 'Inference', 'Concept'],
            # TNS keypaths
            ['alert_identifier'],
            ['message', 'discoverer'],
            ['message', 'name'],
            ['message', 'objname'],
            ['message', 'hostname'],
            ['message', 'internal_name'],
            ['message', 'internal_names'],
            # GCN/LVC Counterpart Notice keypaths,
            ['message', 'telescope'],
            ['message', 'submitter'],
            ['message', 'comments'],
            ['message', 'title'],
        ]
        # a Q-object query looks like Q(key1__key2__ ... __icontains=query_keyword)
        # for dynamic Q-object creation use **kwargs,  like this: Q(**{"keypath__icontains" : query_keyword})
        # Q-object instances can be OR'ed together with '|'

        # create a Q-object query for each keyword in each of the pre-defined keypaths
        aggregate_keyword_query = Q()  # empty Q-object doesn't even add WHERE clause to SQL
        for query_keyword in query_keywords:
            for keypath in keypaths:
                keypath_key = "__".join(keypath + ['icontains'])  # 'keypath[0]__keypath[1]__icontains'
                query = Q(**{keypath_key: query_keyword})
                aggregate_keyword_query = aggregate_keyword_query | query

        return queryset.filter(aggregate_keyword_query)
