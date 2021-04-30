"""skip_base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path, re_path

from skip_base.views import Index


urlpatterns = [
    # Wire up our API using automatic URL routing.
    # Additionally, we include login URLs for the browsable API.
    url('^admin/', admin.site.urls),
    url('^api/', include('skip.urls', namespace='v0')),
    re_path('^api/v1/', include('skip.urls', namespace='v1')),
    re_path('^api/v2/', include('skip.urls', namespace='v2')),
    url('^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    url('^', include('skip_dpd.urls', namespace='skip-dash')),
]
