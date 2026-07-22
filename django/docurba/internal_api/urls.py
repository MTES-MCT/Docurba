from rest_framework import routers

from docurba.internal_api import views

app_name = "internal_api"

router = routers.DefaultRouter()
router.register(r"collectivites", views.CollectiviteViewSet, basename="collectivites")
router.register(r"communes", views.CommuneViewSet, basename="communes")
router.register(r"types-evenement", views.EventTypeViewSet, basename="event_types")
router.register(r"evenements", views.EventViewSet, basename="events")

urlpatterns = router.urls
