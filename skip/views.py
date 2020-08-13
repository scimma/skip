from rest_framework import pagination
from rest_framework import permissions
from rest_framework import viewsets

from skip.filters import AlertFilter
from skip.models import Alert, Target, Topic
from skip.serializers import TargetSerializer, AlertSerializer, TopicSerializer


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
    permission_classes = [permissions.IsAuthenticated]
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer


class TopicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
