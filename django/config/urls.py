from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseNotFound
from django.urls import include, path, re_path
from revproxy.views import ProxyView

from docurba.core import views as core_views

nuxt_proxy = ProxyView.as_view(upstream=settings.UPSTREAM_NUXT)

urlpatterns = [
    path("_admin/", admin.site.urls),
    path("collectivite/<collectivite_code>/", core_views.collectivite),
    path(
        "collectivite/<collectivite_code>/<collectivite_type>/",
        core_views.collectivite,
        name="collectivite-detail",
    ),
    path("api/perimetres", core_views.api_perimetres),
    path("api/communes", core_views.api_communes),
    path("api/scots", core_views.api_scots, name="api_scots"),
    # URLs Nuxt globales
    path("", nuxt_proxy, {"path": ""}),
    re_path(r"(?P<path>^_content.*)", nuxt_proxy),
    re_path(r"(?P<path>^_nuxt.*)", nuxt_proxy),
    re_path(r"(?P<path>^api.*)", nuxt_proxy),
    # URLs Nuxt dans nuxt/static
    re_path(r"(?P<path>^favicon.*)", nuxt_proxy),
    re_path(r"(?P<path>^fonts.*)", nuxt_proxy),
    re_path(r"(?P<path>^images.*)", nuxt_proxy),
    re_path(r"(?P<path>^json.*)", nuxt_proxy),
    re_path(r"(?P<path>^pdf.*)", nuxt_proxy),
    re_path(r"(?P<path>^ressources.*)", nuxt_proxy),
    re_path(r"(?P<path>^sw.js)", nuxt_proxy),
    # URLs Nuxt trouvées via this.$router.options.routes
    re_path(r"(?P<path>^accessibilite.*)", nuxt_proxy),
    re_path(r"(?P<path>^bureau-etude-urbanisme.*)", nuxt_proxy),
    re_path(r"(?P<path>^collectivites.*)", nuxt_proxy),
    re_path(r"(?P<path>^confidentialite.*)", nuxt_proxy),
    re_path(r"(?P<path>^ddt.*)", nuxt_proxy),
    re_path(r"(?P<path>^dev.*)", nuxt_proxy),
    re_path(r"(?P<path>^documents.*)", nuxt_proxy),
    re_path(r"(?P<path>^exports.*)", nuxt_proxy),
    re_path(r"(?P<path>^frise.*)", nuxt_proxy),
    re_path(r"(?P<path>^guide.*)", nuxt_proxy),
    re_path(r"(?P<path>^login.*)", nuxt_proxy),
    re_path(r"(?P<path>^loi-climat-et-resilience.*)", nuxt_proxy),
    re_path(r"(?P<path>^mentions-legales.*)", nuxt_proxy),
    re_path(r"(?P<path>^print.*)", nuxt_proxy),
    re_path(r"(?P<path>^stats.*)", nuxt_proxy),
    re_path(r"(?P<path>^trames.*)", nuxt_proxy),
    re_path(r"(?P<path>^validation.*)", nuxt_proxy),
]

if settings.DEBUG:
    urls = [
        path(  # Désactive le websocket hot reload Nuxt en dev
            "_content/ws", lambda _: HttpResponseNotFound()
        ),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        from debug_toolbar.toolbar import debug_toolbar_urls

        urls += debug_toolbar_urls()

    if "django_browser_reload" in settings.INSTALLED_APPS:
        urls.append(path("__reload__/", include("django_browser_reload.urls")))

    urlpatterns = [*urls, *urlpatterns]
