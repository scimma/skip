from django.http import HttpResponse
from django.urls import reverse

from rest_framework import viewsets
from rest_framework import permissions

from skip.models import Event, Target
from skip.serializers import TargetSerializer, EventSerializer


def index(request):
    return HttpResponse(f"You're at the skip index. The API root is here: {reverse('api_root')}")


class TargetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows targets to be viewed or edited.
    """
    # TODO: should we order Targets ?
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]