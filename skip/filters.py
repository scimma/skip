from django_filters import rest_framework as filters


class AlertFilter(filters.FilterSet):
    alert_timestamp = filters.DateTimeFromToRangeFilter()
    role = filters.CharFilter()
    ordering = filters.OrderingFilter(
        fields=(
            ('alert_timestamp', 'alert_timestamp')
        )
    )