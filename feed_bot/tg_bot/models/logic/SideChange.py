from django.db import models

import time

from .LogicModel import LogicModel

class SideChange(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)

    at_score = models.CharField(max_length=5096, default="")

    epoch_time = models.CharField(max_length=5096, default="")

    left_team_after_id = models.IntegerField(default=-1)

    def happen(self, event_id, period_id, at_score):
        
        from .event.Event import Event

        from .Period import Period

        self.event_id = event_id
        self.period_id = period_id
        self.at_score = at_score

        self.save()

        if self.period_id == -1:
            
            period = Period._get_({"event_id": self.event_id})[-1] #TODO return check by status
            period.left_team_id, period.right_team_id = period.right_team_id, period.left_team_id
            period.original_left_team_id, period.original_right_team_id = period.original_right_team_id, period.original_left_team_id
            period.save()

            event = Event._get_({"id": self.event_id})[0]
            event.side_changes_ids += f"{self.id};"
            event.save()

        else:
            period = Period._get_({"id": self.period_id})[0]
            period.left_team_id, period.right_team_id = period.right_team_id, period.left_team_id
            period.side_changes_ids = period.side_changes_ids + str(self.id) + ";"
            period.save()

        self.left_team_after_id = period.left_team_id
        self.epoch_time = str(time.time())
        self.save()

    def cancel_happen(self):
        pass