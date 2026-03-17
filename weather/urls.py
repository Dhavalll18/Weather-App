from django.urls import path

from .views import get_weather, home

urlpatterns = [
    path("", home, name="home"),
    path("get-weather/", get_weather, name="get_weather"),
]
