from django.db.models import F
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import viewsets

from skip.filters import AlertFilter, EventFilter, TopicFilter
from skip.models import Alert, Event, Target, Topic
from skip.serializers import AlertSerializer, EventDetailSerializer, EventSerializer, TargetSerializer, TopicSerializer


class TargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows targets to be viewed or edited.
    """
    # TODO: should we order Targets ?
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = pagination.PageNumberPagination


class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    filterset_class = AlertFilter
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

    class Meta:
        ordering = [F('alert_timestamp').desc(nulls_last=True)]  # https://docs.djangoproject.com/en/dev/ref/models/options/#ordering


class TopicViewSet(viewsets.ModelViewSet):
    filterset_class = TopicFilter
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class EventViewSet(viewsets.ModelViewSet):
    filterset_class = EventFilter
    queryset = Event.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer
