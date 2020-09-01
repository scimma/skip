import math

from django_filters import rest_framework as filters
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.contrib.gis.measure import D

from skip.models import Topic


EARTH_RADIUS_METERS = 6371008.77141506


class AlertFilter(filters.FilterSet):
    # keyword = filters.CharFilter(method='filter_keyword_search', label='Keyword Search', help_text='Text Search')
    cone_search = filters.CharFilter(method='filter_cone_search', label='Cone Search', 
                                     help_text='RA, Dec, Radius (degrees)')
    polygon_search = filters.CharFilter(method='filter_polygon_search', label='Polygon Search',
                                        help_text='Comma-separated pairs of space-delimited coordinates (degrees).')
    alert_timestamp = filters.DateTimeFromToRangeFilter()
    role = filters.ChoiceFilter(choices=(('utility', 'Utility'), ('test', 'Test'), ('observation', 'Observation')),
                                null_label='None')
    topic = filters.ModelMultipleChoiceFilter(queryset=Topic.objects.all())
    ordering = filters.OrderingFilter(
        fields=(
            ('alert_timestamp', 'alert_timestamp')
        )
    )

    def filter_cone_search(self, queryset, name, value):
        ra, dec, radius = value.split(',')

        ra = float(ra)
        dec = float(dec)

        radius_meters = 2 * math.pi * EARTH_RADIUS_METERS * float(radius) / 360

        return queryset.filter(coordinates__distance_lte=(Point(ra, dec), D(m=radius_meters)))

    def filter_polygon_search(self, queryset, name, value):
        value += ', ' + value.split(', ', 1)[0]
        vertices = tuple((float(v.split(' ')[0]), float(v.split(' ')[1])) for v in value.split(', '))
        polygon = Polygon(vertices, srid=4035)
        return queryset.filter(coordinates__within=polygon)

    # def filter_keyword_search(self, queryset, name, value):
    #     print(value)
    #     return queryset.filter(message__search=value)
