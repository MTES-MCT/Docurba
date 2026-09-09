from django.urls import path

from docurba.api import views

app_name = "api"

urlpatterns = [
    path("perimetres", views.perimetres, name="perimetres"),
    path("communes", views.communes, name="communes"),
    path("scots", views.scots, name="scots"),
]
