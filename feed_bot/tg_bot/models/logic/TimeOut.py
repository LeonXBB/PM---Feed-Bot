from django.db import models

import time

from .LogicModel import LogicModel

class TimeOut(LogicModel):

    is_technical = models.IntegerField(default=0)

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)
    
    at_score = models.CharField(max_length=5096, default="")

    epoch_time = models.CharField(max_length=5096, default="")

    def happen(self, event_id, period_id, team_id, at_score):

        from .Period import Period

        self.event_id = event_id
        self.period_id = period_id
        self.team_id = team_id
        self.at_score = at_score
        self.epoch_time = str(time.time())
        self.save()

        period = Period._get_({"id":self.period_id})[0]
        period.timeouts_ids = period.timeouts_ids + str(self.id) + ";"
        period.save()

    def cancel_happen(self):
        pass