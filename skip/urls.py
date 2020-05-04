from django.urls import include, path

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'targets', views.TargetViewSet)
router.register(r'events', views.EventViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls), name='api_root'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
