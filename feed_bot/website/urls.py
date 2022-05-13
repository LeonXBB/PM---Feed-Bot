from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name="index"),
    path('ping', views.Ping.as_view(), name="ping")
]