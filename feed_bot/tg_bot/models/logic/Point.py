from django.db import models

import time

from .LogicModel import LogicModel


class Point(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)

    at_score = models.CharField(max_length=5096, default="")
    
    epoch_time = models.CharField(max_length=5096, default="")

    type = models.IntegerField(default=-1)
    value = models.IntegerField(default=1)

    def happen(self, event_id, period_id, team_id, at_score, type):
        
        self.event_id = event_id
        self.period_id = period_id
        self.team_id = team_id
        self.at_score = at_score
        self.type = type
        self.epoch_time = str(time.time())
        self.save()

    def cancel_happen(self):
        pass 