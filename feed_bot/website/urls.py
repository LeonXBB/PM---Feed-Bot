from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_ind', views.Index.as_view(), name="index")
]