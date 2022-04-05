from django.db import models

import time

from .LogicModel import LogicModel


class Action(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)
    type_id = models.IntegerField(default=-1)

    epoch_time = models.CharField(max_length=5096, default="")

    at_score = models.CharField(max_length=5096, default="")

    def happen(self, event_id, period_id, team_id, type_id, at_score):
        
        from ..logic.Period import Period

        self.event_id = event_id
        self.period_id = period_id
        self.team_id = team_id
        self.type_id = type_id
        self.at_score = at_score
        self.epoch_time = str(time.time())
        self.save()

        period = Period._get_({"id": self.period_id})[0]
        period.actions_ids = period.actions_ids + str(self.id) + ";"
        period.save()

    def cancel_happen(self):
        
        from ..logic.Period import Period

        self.status = 0
        self.save()
        
        period = Period._get_({"id": self.period_id})[0]
        period.actions_ids.pop(f";{self.id};")
        period.save()

        period.cancel("")