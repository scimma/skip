from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from skip import views

app_name = 'skip'

router = DefaultRouter()
router.register(r'targets', views.TargetViewSet)
router.register(r'alerts', views.AlertViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'events', views.EventViewSet)


urlpatterns = [
    url('', include((router.urls, 'skip'), namespace='skip')),
]
