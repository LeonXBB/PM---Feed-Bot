from django.db import models

import time

from ...bin.utils import Utils

from .LogicModel import LogicModel


class CoinToss(LogicModel):
    
    event_id = models.IntegerField(default=-1)

    epoch_scheduled = models.CharField(max_length=5096, default="")
    epoch_actual = models.CharField(max_length=5096, default="") 

    before_period = models.IntegerField(default=1)

    left_team_id = models.IntegerField(default=0)
    ball_possesion_team_id = models.IntegerField(default=0)

    def happen(self, event_id, epoch_scheduled, before_period, team_id):
        
        self.event_id = event_id
        self.epoch_scheduled = epoch_scheduled
        self.before_period = before_period
        self.left_team_id = team_id
        self.ball_possesion_team_id = team_id

        self.save()

    def swipe(self, attr):

        from .event.Event import Event

        from .Period import Period

        event = Event._get_({"id": self.event_id})[0]

        setattr(self, attr, event.away_team_id if getattr(self, attr) == event.home_team_id else event.home_team_id)

        self.save()
        
        Utils.api("coin_toss_edited", "logic", event_id=self.event_id, period_count=len(Period._get_({"event_id": self.event_id})), coin_toss_id=self.id, coin_toss_count=len(CoinToss._get_({"event_id": self.event_id})), attr=attr, val=getattr(self, attr))

        return self.show_template()

    def save_results(self):
        
        from .event.Event import Event
        
        from .Period import Period

        event = Event._get_({"id": self.event_id})[0]

        self.epoch_actual = str(time.time())
        self.save()

        new_period = Period()
        new_period.event_id = self.event_id
        
        new_period.left_team_id = self.left_team_id
        new_period.right_team_id = (event.home_team_id if self.left_team_id == event.away_team_id else event.away_team_id)
        new_period.ball_possesion_team_id = self.ball_possesion_team_id
        
        new_period.original_left_team_id = self.left_team_id
        new_period.original_right_team_id = (event.home_team_id if self.left_team_id == event.away_team_id else event.away_team_id)
        new_period.original_ball_possesion_team_id = self.ball_possesion_team_id

        new_period.save()

        Utils.api("coin_toss_saved", "logic", event_id=self.event_id, period_id=new_period.id, period_count=len(Period._get_({"event_id": self.event_id})), coin_toss_id=self.id, coin_toss_count=len(CoinToss._get_({"event_id": self.event_id})), left_team_id=self.left_team_id, ball_possession_team_id=self.ball_possesion_team_id)

        return new_period.start() 
        
    def cancel_happen(self):
        pass

    def cancel_edit(self):
        pass

    def cancel_save(self):
        pass

    def show_template(self):

        from .event.Event import Event

        from .Team import Team

        from ..telebot.BotUser import BotUser

        event = Event._get_({"id": self.event_id})[0]
        admin = BotUser._get_({"id": event.admin_id})[0]
        
        left_team_name = Team._get_({"id": self.left_team_id})[0].name
        server_name = Team._get_({"id": self.ball_possesion_team_id})[0].name

        rv = []
        rv.append(admin.show_screen_to("32", [[self.event_id, self.before_period, left_team_name, server_name], ], [[self.id, self.id, self.id, self.id], ]))
        rv.append(("ignore", 32))
        return rv