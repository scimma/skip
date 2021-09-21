from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from hop import Stream
from hop.auth import Auth
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action

from skip.filters import AlertFilter, EventFilter, TopicFilter
from skip.models import Alert, Event, Target, Topic
from skip.serializers import AlertSerializer, EventDetailSerializer, EventSerializer, TargetSerializer, TopicSerializer
from skip.serializers.v1 import serializers as v1_serializers


class TargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows targets to be viewed or edited.
    """
    # TODO: should we order Targets ?
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = pagination.PageNumberPagination


class AlertViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    filterset_class = AlertFilter
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

    class Meta:
        # https://docs.djangoproject.com/en/dev/ref/models/options/#ordering
        ordering = [F('alert_timestamp').desc(nulls_last=True), F('timestamp').desc(nulls_last=True)]

    def get_serializer_class(self):
        if self.request.version in ['v0', 'v1']:
            return v1_serializers.AlertSerializer
        return AlertSerializer

    @action(detail=False, methods=['post'])
    def submit(self, request, *args, **kwargs):
        auth = Auth(
            settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.username'],
            settings.HOPSKOTCH_CONSUMER_CONFIGURATION['sasl.password']
        )
        stream = Stream(auth=auth)

        topic = request.data.pop('topic')
        with stream.open(f'kafka://{settings.HOPSKOTCH_SERVER}:{settings.HOPSKOTCH_PORT}/{topic}', 'w') as s:
            s.write(request.data)
        return HttpResponse(f'Successfully submitted alert to {topic}.')


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
