from django.conf import settings
from django.urls import re_path
from revproxy.views import ProxyView

urlpatterns = [
    re_path(r"(?P<path>.*)", ProxyView.as_view(upstream=settings.UPSTREAM_NUXT)),
]
