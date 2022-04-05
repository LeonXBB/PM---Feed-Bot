from django.db import models

from ..LogicModel import LogicModel


class EventTemplateEdit(LogicModel): #TODO move template to different class and change all references to it

    event_id = models.IntegerField(default=-1)
    field_name = models.CharField(max_length=5096)
    old_value = models.CharField(max_length=5096)
    new_value = models.CharField(max_length=5096)

    def undo(seld):
        pass