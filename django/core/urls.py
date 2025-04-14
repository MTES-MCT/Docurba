from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from revproxy.views import ProxyView

from core import views

urlpatterns = [
    path("_admin/", admin.site.urls),
    path("collectivite/<collectivite_code>/", views.collectivite),
    path(
        "collectivite/<collectivite_code>/<collectivite_type>/",
        views.collectivite,
        name="collectivite-detail",
    ),
    path("api/perimetres", views.api_perimetres),
    path("api/scots", views.api_scots),
    path("__reload__/", include("django_browser_reload.urls")),
    *debug_toolbar_urls(),
    re_path(r"(?P<path>.*)", ProxyView.as_view(upstream=settings.UPSTREAM_NUXT)),
]
