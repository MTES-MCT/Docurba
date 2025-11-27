from rest_framework import routers

from docurba.internal_api import views

app_name = "internal_api"

router = routers.DefaultRouter()
router.register(r"collectivites", views.CollectiviteViewSet, basename="collectivites")
router.register(r"communes", views.CommuneViewSet, basename="communes")

urlpatterns = router.urls
