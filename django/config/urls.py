from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from docurba.core import views as core_views

urlpatterns = [
    path("_admin/", admin.site.urls),
    path("collectivite/<collectivite_code>/", core_views.collectivite),
    path(
        "collectivite/<collectivite_code>/<collectivite_type>/",
        core_views.collectivite,
        name="collectivite-detail",
    ),
    path("api/perimetres", core_views.api_perimetres, name="api_perimetres"),
    path("api/communes", core_views.api_communes, name="api_communes"),
    path("api/scots", core_views.api_scots, name="api_scots"),
    path("api-internes/", include("docurba.internal_api.urls")),
]

if settings.DEBUG:
    urls = []
    if "debug_toolbar" in settings.INSTALLED_APPS:
        from debug_toolbar.toolbar import debug_toolbar_urls

        urls += debug_toolbar_urls()

    if "django_browser_reload" in settings.INSTALLED_APPS:
        urls.append(path("__reload__/", include("django_browser_reload.urls")))

    urlpatterns = [*urls, *urlpatterns]
