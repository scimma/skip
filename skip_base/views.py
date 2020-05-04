from django.views.generic import RedirectView
from django.urls import reverse_lazy


class Index(RedirectView):
    url = reverse_lazy('skip:api-root')
