from django.urls import path
from rest_framework import routers

from docurba.internal_api import views

app_name = "internal_api"

router = routers.DefaultRouter()
router.register(r"collectivites", views.CollectiviteViewSet, basename="collectivites")
router.register(r"communes", views.CommuneViewSet, basename="communes")
router.register(r"types-evenement", views.EventTypeViewSet, basename="event_types")

urlpatterns = [
    path(
        "users/user_must_update_password",
        views.UserMustUpdatePasswordView.as_view(),
        name="user_must_update_password",
    ),
    path(
        "users/password",
        views.UserPassword.as_view(),
        name="user-password",
    ),
    *router.urls,
]
