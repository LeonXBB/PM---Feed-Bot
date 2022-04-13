from django.urls import path

from .consumers import RulesSetConsumer, EventsListConsumer

ws_urlpatterns = [
    path('ws/get_rules_sets/', RulesSetConsumer.as_asgi()),
    path('ws/get_events_list/', EventsListConsumer.as_asgi()),
]