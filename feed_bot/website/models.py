from django.db import models

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import time

class APIMessage(models.Model):
    
    event_id = models.IntegerField(default=-1)
    message = models.CharField(max_length=5096)
    hour = models.CharField(default=-1, max_length=2)
    minute = models.CharField(default=-1, max_length=2)
    second = models.CharField(default=-1, max_length=2)   
    score_1 = models.IntegerField(default=-1)
    score_2 = models.IntegerField(default=-1)

    def __repr__(self):
        return self.message

    def add(self, event_id, message):
        
        from tg_bot.models import Event, Period, Point

        self.event_id = event_id
        self.message = message

        self.hour = time.strftime("%H")
        self.minute = time.strftime("%M")
        self.second = time.strftime("%S")

        event = Event._get_({"id": event_id})[0]
        
        score = [0, 0]

        try:        
            last_period_id = list(period_id for period_id in event.periods_ids.split(";") if period_id)[-1]
            last_period = Period._get_({"id": int(last_period_id)})[0]

            for point_id in list(point_id for point_id in last_period.points_ids.split(";") if point_id):
                if point_id:
                    point = Point._get_({"id": int(point_id)})[0]
                    score[0 if point.team_id == event.home_team_id else 1] += point.value
        except:
            pass

        self.score_1 = score[0]
        self.score_2 = score[1]

        self.save()

    def send(self):

        if not hasattr(self, "channel_layer"):
            self.channel_layer = get_channel_layer()

        async_to_sync(self.channel_layer.group_send)(
            f'event_data_{self.event_id}',
            {"type": "update.messages", "time": f"{self.hour}:{self.minute}:{self.second}", "scores": f"{self.score_1}:{self.score_2}", "message": self.message}
        )
