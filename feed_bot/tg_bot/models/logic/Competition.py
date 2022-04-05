from django.db import models

from .LogicModel import LogicModel


class Competition(LogicModel):

    name = models.CharField(max_length=5096, default="")
    events_ids = models.CharField(max_length=5096, default=";")