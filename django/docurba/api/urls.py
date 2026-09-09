from django.urls import path

from docurba.api import views

app_name = "api"

urlpatterns = [
    path("perimetres", views.PerimetresView.as_view(), name="perimetres"),
    path("communes", views.CommunesView.as_view(), name="communes"),
    path("scots", views.ScotsView.as_view(), name="scots"),
]
