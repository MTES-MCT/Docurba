from rest_framework import routers

from core.api_internes import views

# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "api_internes"

router = routers.DefaultRouter()
router.register(r"collectivites", views.CollectiviteViewSet, basename="collectivites")
router.register(r"communes", views.CommuneViewSet, basename="communes")

urlpatterns = router.urls
