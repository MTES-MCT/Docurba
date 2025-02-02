from django.conf import settings
from django.urls import include, path, re_path
from revproxy.views import ProxyView

from core import views

urlpatterns = [
    path("api/perimetres", views.perimetres),
    path("__reload__/", include("django_browser_reload.urls")),
    # re_path(r"(?P<path>.*)", ProxyView.as_view(upstream=settings.UPSTREAM_NUXT)),
]
