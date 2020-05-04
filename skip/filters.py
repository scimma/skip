from django_filters import rest_framework as filters


class EventFilter(filters.FilterSet):
    event_timestamp = filters.DateTimeFromToRangeFilter()
    topic = filters.CharFilter()
    role = filters.CharFilter()
    ordering = filters.OrderingFilter(
        fields=(
            ('event_timestamp', 'event_timestamp')
        )
    )