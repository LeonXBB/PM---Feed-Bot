from django.urls import path

from . import views

urlpatterns = [
    path('api', views.BotAPI.as_view(), name="index"),
    path('api/logic', views.BotLogicAPI.as_view(), name="logic")
]