from typing import List
from decouple import config

from django.db import models

import hashlib
import time
import datetime

from .screens.Screen import Screen
from .screens.remainders.Remainder import Remainder

# Create your models here.

#LOGIC #TODO sepatate by different files

class LogicModel(models.Model):
    
    @classmethod
    def _get_(cls, params):
        
        rv = []
        
        for obj in cls.objects.all():
            for k,v in params.items():
                if getattr(obj, k) == v:
                    rv.append(obj)

        return rv

    created = models.CharField(max_length=5096, default=";") # user_id, timestamp
    status = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def _cancel_(self):
        self.status = 5

class Event(LogicModel):  #TODO move template to different class?
    
    # statuses: 0 - being created, 1 - awaiting start, 2 - ongoing, 3 - between periods, 4 - finished
    
    active_status = models.IntegerField(default=1)

    admin_id = models.IntegerField(default=-1)

    competition_id = models.IntegerField(default=-1)
    rules_set_id = models.IntegerField(default=-1)

    date_scheduled =  models.CharField(max_length=5096, default="")
    time_scheduled = models.CharField(max_length=5096, default="")
   
    start_scheduled_epoch = models.CharField(max_length=5096, default="")
    start_actual_epoch = models.CharField(max_length=5096, default="")
    end_scheduled_epoch = models.CharField(max_length=5096, default="")
    end_actual_epoch = models.CharField(max_length=5096, default="")

    home_team_id = models.IntegerField(default=-1)
    away_team_id = models.IntegerField(default=-1)

    periods_ids = models.CharField(max_length=5096, default=";")

    coin_toss_ids = models.CharField(max_length=5096, default=";")
    side_changes_ids = models.CharField(max_length=5096, default=";")

    # CREATE TEMPLATE 

    def make_template(self): #TODO DO and JSON
        pass

    def show_template(self): #TODO JSON

        home_team_name = "" if self.home_team_id == -1 else Team._get_({"id": self.home_team_id})[0].name 
        away_team_name = "" if self.away_team_id == -1 else Team._get_({"id": self.away_team_id})[0].name 
        
        competition_name = "" if self.competition_id == -1 else Competition._get_({"id": self.competition_id})[0].name  
        rules_set_name = "" if self.rules_set_id == -1 else RulesSet._get_({"id": self.rules_set_id})[0].name      

        formatters = (str(self.id), home_team_name, away_team_name, competition_name, rules_set_name, self.date_scheduled, self.time_scheduled)
        
        ready = True
        for x in formatters:
            if len(x) == 0:
                ready = False
                break

        if ready:
            return BotUser._get_({"id": self.admin_id})[0].show_screen_to("20", [formatters,])
        else:
            return BotUser._get_({"id": self.admin_id})[0].show_screen_to("21", [formatters,])

    def edit_template(self): #TODO DO and JSON
        pass

    def cancel_edit_template(self): #TODO DO and JSON
        pass

    def save_template(self): #TODO JSON
        
        '''home_team_name = Team._get_({"id": self.home_team_id})[0].name
        away_team_name = Team._get_({"id": self.away_team_id})[0].name
        
        self.status = 1
        self.save()

        admin = BotUser._get_({"id": self.admin_id})[0]

        rv = []

        rv.append(admin.show_screen_to("10", [[config("telebot_version")], ], ))
        #TODO move static formatters into screen class?

        rv.extend(Remainder._get_("EventScheduled").schedule([int(time.time()), int(time.time()) + 15], self.admin_id, [[self.id, home_team_name, away_team_name],[]], f"event_{self.id}_start", [[self.id, self.id], ]))'''
        
        rv = self.start()

        return rv

    def cancel_save(self): #TODO DO and JSON
        pass

    # MATCH TEMPLATE

    def show_match_template(self):
        # TODO remember about callback data for buttons
        print(f"showing match template for event # {self.id}")
        return BotUser._get_({"id": self.admin_id})[0].show_list_of_events()

    # LOGIC

    def start(self): #TODO JSON
        
        rules_set = RulesSet._get_({"id": self.rules_set_id})[0]

        admin = BotUser._get_({"id": self.admin_id})[0]

        self.status = 1

        day, month, year = self.date_scheduled.split("-")
        hour, minute = self.time_scheduled.split(":")

        self.start_scheduled_epoch = str(int(datetime.datetime(int(year), int(month), int(day), int(hour), int(minute)).timestamp()))   

        print(datetime.datetime(int(year), int(month), int(day), int(hour), int(minute)).timestamp())
        print(datetime.datetime(int(year), int(month), int(day), int(hour), int(minute)))

        if rules_set.event_length_minutes == 0:
            self.end_scheduled_epoch= "0"
        else:
   
            end_time = str(int(self.start_scheduled_epoch) + int(rules_set.event_length_minutes) * 60)
            self.end_scheduled_epoch = end_time

        self.save()
        
        rv = [admin.show_screen_to("10", [[config("telebot_version")], ], ), *self.run()]

        return rv

    def end(self): #TODO JSON
        
        self.status = 4
        self.end_actual_epoch = int(time.time())
        self.save()
        
        admin = BotUser._get_({"id": self.admin_id})[0]
        return admin.show_screen_to("10", [[config("telebot_version")], ]) #TODO static formatter

    def run(self, command="_"): #TODO JSON
        
        rv = []

        rules_set = RulesSet._get_({"id": self.rules_set_id})[0]

        home_team_name = Team._get_({"id": self.home_team_id})[0].name
        away_team_name = Team._get_({"id": self.away_team_id})[0].name

        period_count = 0
        for period_id in self.periods_ids.split(";"):
            if period_id:
                period_count += 1

        def check_remainders():

            def check_sent_already(remainder_id, group_name):
                return len(ScheduledMessage._get_({"content_id": remainder_id, "group_name": group_name})) > 0
            
            #check coin_toss
            if rules_set.coin_tosses_before_periods.split(";")[period_count] == "1":
                
                if not check_sent_already(140, f"event_{self.id}_coin_toss_{period_count}"):
                    
                    when = int(self.start_scheduled_epoch) - int(rules_set.coin_toss_start_before_minutes.split(";")[len(CoinToss.objects.all())]) * 60
                    
                    rv.extend(Remainder._get_("CoinTossHappens").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_coin_toss_{period_count}", [[self.id, self.id], ]))

                    for offset in rules_set.coin_toss_remainder_minutes_before.split(";"):
                        if offset:
                            rv.extend(Remainder._get_("CoinTossAboutToHappen").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_coin_toss_{period_count}", [[self.id, self.id], ]))
            
            # check event start
            
            if self.status == 1 and not check_sent_already(100, f"event_{self.id}_start") and not rules_set.coin_tosses_before_periods.split(";")[period_count] == "1":
                    
                when = int(self.start_scheduled_epoch)
                
                rv.extend(Remainder._get_("EventScheduled").schedule(int(time.time()), self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

                rv.extend(Remainder._get_("EventStart").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_start", [[self.id, self.id], ]))
    
                for offset in rules_set.event_start_remainder_minutes_before.split(";"):
                    if offset:
                        rv.extend(Remainder._get_("EventAboutToStart").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

            # check event end

            if rules_set.event_length_minutes != 0 and self.status == 2 and not check_sent_already(101, f"event_{self.id}_start"):
                    
                when = int(self.end_scheduled_epoch)
                
                rv.extend(Remainder._get_("EventEnd").schedule(when, self.admin_id, [[self.id, home_team_name, away_team_name] ,], f"event_{self.id}_end", [[self.id, self.id], ]))
    
                for offset in rules_set.event_end_remainder_minutes_before.split(";"):
                    if offset:
                        rv.extend(Remainder._get_("EventAboutToEnd").schedule(when - int(offset) * 60, self.admin_id, [[self.id, home_team_name, away_team_name, offset] ,], f"event_{self.id}_start", [[self.id, self.id], ]))

            # check side change reminders
            # if it's between periods and it's time to change sides and not sent yet
            if self.status == 3 and rules_set.side_changes_after_periods.split(';')[period_count - 1] == 1 and not check_sent_already(150, f"event_{self.id}_side_change_after_perid_{period_count}"):
                rv.extend((Remainder._get_("SideChangeHappens").schedule(int(time.time()), self.admin_id, [[] ,], f"event_{self.id}_side_change_after_perid_{period_count}", [[], ])))

        def check_coin_toss():
            return data[0] == "coinToss"

        def check_end():
            
            point_score = {self.home_team_id: {} , self.away_team_id: {}}

            for period_id in self.periods_ids:
                if period_id:
                    period = Period._get_({"id": period_id})[0]
                    for point_id in period.points_ids:
                        if point_id:
                            point = Point._get_({"id": point_id})[0]
                            if period_id not in List(point_score[point.team_id].keys()):
                                point_score[point.team_id][period_id] = 0
                            
                            point_score[point.team_id][period_id] += point.score

            def check_end_by_score_period():
                
                int_score = [0, 0]

                for period_id in self.periods_ids.split(";"):
                    if period_id:
                        if point_score[self.home_team_id][period_id] > point_score[self.home_team_id][period_id]:
                            int_score[0] += 1
                        elif point_score[self.home_team_id][period_id] < point_score[self.home_team_id][period_id]:
                            int_score[1] += 1
                        else:
                            int_score[0] += 1
                            int_score[1] += 1

                return rules_set.win_event_by == 2 and (((max(int_score) >= rules_set.periods_to_win_event and rules_set.stop_event_after_enough_periods == 1) or max(int_score) > rules_set.periods_in_event) and max(int_score) - min(int_score) > rules_set.min_difference_to_win_event)

            def check_end_by_score_sum():

                score_sum = [0, 0]

                for period_id in self.periods_ids.split(";"):
                    if period_id:
                        score_sum[0] += point_score[self.home_team_id][period_id]
                        score_sum[1] += point_score[self.away_team_id][period_id]

                return rules_set.win_event_by == 2 and (((score_sum >= rules_set.periods_to_win_event and rules_set.stop_event_after_enough_periods == 1) or max(score_sum) > rules_set.periods_in_event) and score_sum - score_sum > rules_set.min_difference_to_win_event)

            return check_end_by_score_period() or check_end_by_score_sum()

        def check_side_change():
            return self.status == 3 and rules_set.side_changes_after_periods.split(';')[period_count - 1] == 1

        data = command.split("_")

        check_remainders()

        if check_end():
            self.end()

        if check_coin_toss():
            
            obj = CoinToss()

            obj.happen(self.id, int(self.start_scheduled_epoch) - int(rules_set.coin_toss_start_before_minutes.split(";")[len(CoinToss.objects.all())]) * 60, period_count+1, self.home_team_id)
            obj.save()

            rv.extend(obj.show_template())

        if check_side_change():
            
            obj = SideChange()

            obj.happen()
            obj.save()

        return rv

    def cancel(self, task): #TODO JSON

        def cancel_event():
            self.active_status = 0
            self.save()
            return BotUser._get_({"id": self.admin_id})[0].show_list_of_events(True)

        def cancel_cancel_event():
            self.active_status = 1
            self.save()
            return BotUser._get_({"id": self.admin_id})[0].show_list_of_events(True)

        def cancel_run():
            pass

        def cancel_start():
            pass

        def cancel_end():
            pass

        return eval(f"cancel_{task}()")

class Period(LogicModel):

    # statuses 0 - awaiting_start, 1 - ongoing, 2 - paused, 3 - finished

    event_id = models.IntegerField(default=-1)

    epoch_scheduled_start = models.CharField(max_length=5096, default="")
    epoch_scheduled_end = models.CharField(max_length=5096, default="")
    epoch_actual_start = models.CharField(max_length=5096, default="")
    epoch_actual_end = models.CharField(max_length=5096, default="")

    left_team_id = models.IntegerField(default=-1)
    right_team_id = models.IntegerField(default=-1)

    is_paused = models.IntegerField(default=0)
    ball_possesion = models.IntegerField(default=-1)

    time_outs_ids = models.CharField(max_length=5096, default=";")
    points_ids = models.CharField(max_length=5096, default=";")
    actions_ids = models.CharField(max_length=5096, default=";")
    side_changes_ids = models.CharField(max_length=5096, default=";")
    timers_ids = models.CharField(max_length=5096, default=";")

    def start(self): #TODO JSON
        
        event = Event._get_({"id": self.event_id})[0]
        rules_set = RulesSet._get_({"id": event.rules_set_id})[0]
        home_team_name = Team._get_({"id": event.home_team_id})[0].name
        away_team_name = Team._get_({"id": event.away_team_id})[0].name

        self.status = 1
        
        self.epoch_actual_start = str(time.time())
        if rules_set.periods_lenght_minutes == 0:
            self.epoch_scheduled_end = "0"
        else:
            end_time = str(time.time() + rules_set.periods_lenght_minutes.split(";")[len(event.periods_ids.split(";")) - 1] * 60)
            self.epoch_scheduled_end = end_time
            
            current_period_number = len(period_id for period_id in event.periods_ids.split(";") if period_id)

            Remainder._get_("PeriodEnd").schedule(end_time, event.admin_id, [[current_period_number, self.event_id, home_team_name, away_team_name],], f"event_{self.event_id}_end", [[self.id,],])
            for event_end_remainder in rules_set.event_end_remainder_minutes_before.split(";"):
                if event_end_remainder:
                    Remainder._get_("PeriodAboutToEnd").schedule(end_time - int(event_end_remainder) * 60, event.admin_id, [[current_period_number, self.event_id, home_team_name, away_team_name],], f"event_{self.event_id}_end", [[self.id,],])

        self.save()

        
        self.run()

    def end(self): #TODO JSON
        
        self.status = 3
        self.epoch_actual_end = str(time.time())
       
        Remainder.unschedule(f"event_{self.event.id}_end")

        self.save()

        event = Event._get_({"id": self.event_id})[0]
       
        event.run()

    def pause(self):
        pass

    def resume(self):
        pass

    def run(self, command="_") -> None: #TODO JSON
        
        def check_period_end():
            pass

        def check_technical_time_out():
            pass

        def check_time_out():
            pass

        def check_side_change():
            pass

        def check_action():
            return data[0] == "action"

        def check_point():
            pass

        def check_pause_resume():
            pass

        data = command.split("_")

        if check_period_end():
            pass

        if check_technical_time_out():
            
            obj = TimeOut()
            obj.is_technical = 1
            obj.happen()
            obj.save()

        if check_time_out():

            obj = TimeOut()
            obj.happen()
            obj.save()

        if check_side_change():

            obj = SideChange()
            obj.happen()
            obj.save()

        if check_action():

            obj = Action()

            obj.event_id = data[1]
            obj.team_id = data[2]
            obj.type_id = data[3]
            obj.save()

            obj.happen()
            
        if check_point():
                
            obj = Point()
            obj.happen()
            obj.save()

        if check_pause_resume():
            pass

    def cancel(self): #TODO JSON
        pass

class Team(LogicModel):
    
    name = models.CharField(max_length=5096, default="")
    events_ids = models.CharField(max_length=5096, default=";") 

class Competition(LogicModel):

    name = models.CharField(max_length=5096, default="")
    events_ids = models.CharField(max_length=5096, default=";")

class RulesSet(LogicModel):
    
    name = models.CharField(max_length=5096, default="")

    win_event_by = models.IntegerField(default=0) #
    win_period_by = models.CharField(max_length=5096, default=';')

    periods_in_event = models.IntegerField(default=2) #
    periods_to_win_event = models.IntegerField(default=2) #

    points_in_period = models.IntegerField(default=2)
    points_to_win_period = models.CharField(max_length=5096, default=';')

    stop_event_after_enough_periods = models.BooleanField(default=False) #
    stop_period_after_enough_points = models.BooleanField(default=False)

    min_difference_periods_to_win_event = models.IntegerField(default=0) #
    min_difference_points_to_win_period = models.CharField(max_length=5096, default=';')

    points_per_score_per_period = models.CharField(max_length=5096, default=';')
    scores_names = models.CharField(max_length=5096, default=';')

    event_length_minutes = models.IntegerField(default=0) # 
    periods_lenght_minutes = models.CharField(max_length=5096, default=';') 

    interval_between_periods_munutes = models.CharField(max_length=5096, default=';')

    event_timer_direction = models.IntegerField(default=0)
    period_timers_directions = models.CharField(max_length=5096, default=';')

    event_timer_stops_at_pauses = models.BooleanField(default=False)
    period_timers_stop_at_pauses = models.CharField(max_length=5096, default=';')

    side_changes_after_periods = models.CharField(max_length=5096, default=';') #
    side_changes_during_periods = models.CharField(max_length=5096, default=';')
    side_changes_during_periods_scores = models.CharField(max_length=5096, default=';')
    side_changes_during_periods_pause_time_seconds = models.CharField(max_length=5096, default=';')
    
    coin_tosses_before_periods = models.CharField(max_length=5096, default=';') #
    coin_toss_start_before_minutes  = models.CharField(max_length=5096, default=';') #

    time_outs_per_team_per_period = models.CharField(max_length=5096, default=';')
    time_outs_lenghts_per_team_per_period = models.CharField(max_length=5096, default=';')
    
    technical_time_outs_lenghts_per_period = models.CharField(max_length=5096, default=';')
    technical_time_outs_at_score_per_period = models.CharField(max_length=5096, default=';')
    
    actions_list = models.CharField(max_length=5096, default=';')
    
    event_start_remainder_minutes_before = models.CharField(max_length=5096, default=';') #
    event_end_remainder_minutes_before = models.CharField(max_length=5096, default=';') #
    period_start_remainder_minutes_before = models.CharField(max_length=5096, default=';')
    period_end_remainder_minutes_before = models.CharField(max_length=5096, default=';')
    coin_toss_remainder_minutes_before = models.CharField(max_length=5096, default=';') #
    
    def register(self):
        pass

    def delete(self):
        pass

class Action(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)
    type_id = models.IntegerField(default=-1)

    epoch_time = models.CharField(max_length=5096, default="")

    at_score = models.CharField(max_length=5096, default="")

    def happen(self):
        
        # at init, given: event_id, team_id, type_id
        # at init_calculate: period_id, at_score, epoch_time

        event = Event._get_(self.event_id)[0]

        self.period_id = event.periods_ids.split(";")[-1] if event.periods_ids.split(";")[-1] else event.periods_ids.split(";")[-2]

        period = Period._get_(self.period_id)[0]

        self.at_score = period.score 
        self.epoch_time = str(time.time())
        self.save()

        period.actions_ids = period.actions_ids + str(self.id) + ";"
        period.save()

        period.run()

    def cancel_happen(self):
        
        self.status = 0
        self.save()
        
        period = Period._get_(self.period_id)[0]
        period.actions_ids.pop(f";{self.id};")
        period.save()

        period.cancel("")

class CoinToss(LogicModel):
    
    event_id = models.IntegerField(default=-1)

    epoch_scheduled = models.CharField(max_length=5096, default="")
    epoch_actual = models.CharField(max_length=5096, default="") 

    before_period = models.IntegerField(default=1)

    left_team_id = models.IntegerField(default=0)
    ball_possesion_team_id = models.IntegerField(default=0)

    # at init, given: event_id, before_period_id
    # at init_calculate: epoch_scheduled, left_team_id, ball_possesion, epoch_actual

    def happen(self, event_id, epoch_scheduled, before_period, team_id):
        
        self.event_id = event_id
        self.epoch_scheduled = epoch_scheduled
        self.before_period = before_period
        self.left_team_id = team_id
        self.ball_possesion_team_id = team_id

        self.save()

    def swipe(self, attr):

        event = Event._get_(self.event_id)[0]

        setattr(self, attr, event.left_team_id if getattr(self, attr) == event.right_team_id else event.left_team_id)
        self.save()
        return self.show_template()

    def save_results(self):
        
        self.epoch_actual = str(time.time())

        self.save()

    def cancel_happen(self):
        pass

    def cancel_edit(self):
        pass

    def cancel_save(self):
        pass

    def show_template(self):

        event = Event._get_({"id": self.event_id})[0]
        admin = BotUser._get_({"id": event.admin_id})[0]
        
        left_team_name = Team._get_({"id": self.left_team_id})[0].name
        server_name = Team._get_({"id": self.ball_possesion_team_id})[0].name

        rv = []
        rv.append(admin.show_screen_to("32", [[self.event_id, self.before_period, left_team_name, server_name], ], [[self.id, self.id], ]))
        rv.append(("ignore", 32))
        return rv

class Point(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)

    at_score = models.CharField(max_length=5096, default="")
    
    epoch_time = models.CharField(max_length=5096, default="")

    point_type = models.IntegerField(default=-1)
    value = models.IntegerField(default=1)

    def happen(self):
        pass

    def cancel_happen(self):
        pass 

class SideChange(LogicModel):

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)

    at_score = models.CharField(max_length=5096, default="")

    epoch_time = models.CharField(max_length=5096, default="")

    left_team_after_id = models.IntegerField(default=-1)

    def happen(self):
        pass

    def cancel_happen(self):
        pass

class TimeOut(LogicModel):

    is_technical = models.IntegerField(default=0)

    event_id = models.IntegerField(default=-1)
    period_id = models.IntegerField(default=-1)
    team_id = models.IntegerField(default=-1)
    
    at_score = models.CharField(max_length=5096, default="")

    epoch_time = models.CharField(max_length=5096, default="")

    team_id = models.IntegerField(default=-1)

    def happen(self):
        pass

    def cancel_happen(self):
        pass

# TELEBOT
class PasswordPair(models.Model):
    
    password_sha256 = models.CharField(max_length=5096)
    user_id = models.IntegerField(default=-1)

    #def generate(self, string): #TODO connect (via superadmin commands?)
    #   self.password_sha256 = hashlib.sha256(string.encode('utf8')).hexdigest()
    #   self.save()
    
    def assign_to_user(self, user_id):
        
        self.user_id = user_id

        users = BotUser.objects.all()
        for user in users:
            if user.id == user_id:
                user.password_id = self.id
                user.save()
        
        self.save()

class BotUser(models.Model):

    tg_id = models.CharField(max_length=5096, blank=True)
    language_id = models.IntegerField(default=0)

    password_id = models.IntegerField(default=-1)
    is_logged_in = models.IntegerField(default=0)
    is_superadmin = models.IntegerField(default=0)

    current_screen_code = models.CharField(max_length=5096, default="00")

    screen_messages_ids = models.CharField(max_length=5096, default=f"{{}}")
    remainders_ids = models.CharField(max_length=5096, default=f"{{}}")
    user_input_messages_ids = models.CharField(max_length=5096, default=f"{{}}")

    @classmethod
    def _get_(cls, params):

        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv

    def check_authorization(self, ignore_authorization_screens=False):
        return self.is_logged_in or ((self.current_screen_code == "00" or self.current_screen_code == "01") and ignore_authorization_screens)

    def receive_text_from(self, text):
        
        if not self.check_authorization(True):
            return self.show_screen_to("00")       

        screen = Screen._get_(id=self.current_screen_code)
            
        return None if not hasattr(screen, "text") else screen.text(text, self.id) 

    def receive_command_from(self, command):
        if not self.check_authorization():
            return self.show_screen_to("00")       

        if command == "/start":
            return self.show_screen_to("10", [[config("telebot_version")], ]) #TODO move static formatters into screen class?
        elif command.startswith('/show_screen'):
            return self.show_screen_to(*command.split(" ")[1:]) if self.is_superadmin else None
        else:    
            return self.receive_text_from(command)

    def receive_button_press_from(self, button_id, params, screen_type, screen_id="", scheduled_message_id=None):
        
        if not self.check_authorization():
            return self.show_screen_to("00")       
        
        if screen_type == "screen":
            
            screen = Screen._get_(id=self.current_screen_code if screen_id == "" else str(screen_id))

            return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id)

        elif screen_type == "remainder":

            screen = Remainder._get_(remainder_id=str(screen_id))
            return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id, scheduled_message_id)

    def show_screen_to(self, screen_id, format_strs=None, callback_data=None):
        self.current_screen_code = screen_id
        self.save()
        return [screen_id, "screen", format_strs, callback_data]

    def send_remainder_to(self, remainder_id, epoch, format_strs=None, group="", callback_data=None):
        return [remainder_id, "remainder", epoch, format_strs, group, callback_data]

    def show_list_of_events(self, flush_safe=False):

        status_strings = []
        for text_string in TextString.objects.all().order_by("id"):
            if text_string.screen_id == "status":
                status_strings.append([text_string.language_1, text_string.language_2, text_string.language_3, text_string.language_4, text_string.language_5])

        rv = []

        for event in Event.objects.all():

            if event.admin_id == self.id:
                
                home_team_name = Team._get_({"id": event.home_team_id})[0].name
                away_team_name = Team._get_({"id": event.away_team_id})[0].name

                competition_name = Competition.objects.get(pk=event.competition_id).name

                rules_set_name = RulesSet.objects.get(pk=event.rules_set_id).name

                date = event.date_scheduled
                time_ = event.time_scheduled

                if event.active_status == 1:
                    rv.append(self.show_screen_to("43", [[event.id, status_strings[event.status][self.language_id], home_team_name, away_team_name, competition_name, rules_set_name, date, time_]], [[event.id, event.id],]))
                else:
                    rv.append(self.show_screen_to("44", [[event.id, status_strings[5][self.language_id], home_team_name, away_team_name, competition_name, rules_set_name, date, time_]], [[event.id, event.id],]))

        if len(rv) > 0:
            rv.append(self.show_screen_to("40", [[], ]))
        else: 
            rv.append(self.show_screen_to("41", [[], ]))

        if flush_safe: rv.append(("ignore", 40, 43, 44))

        return rv

class ScheduledMessage(models.Model):

    @classmethod
    def _get_(cls, params):

        rv = []

        for obj in cls.objects.all():
            
            true = True
            for k, v in params.items():
                if getattr(obj, k) != v:
                    true = False
            
            if true: rv.append(obj)

        return rv

    user_id = models.IntegerField(default=-1)
    messages_ids = models.CharField(max_length=5096, default=";")

    epoch = models.CharField(max_length=5096, default="")
    pause_epoch = models.CharField(max_length=5096, default="")

    content_type = models.CharField(max_length=5096, default="remainder")
    content_id = models.IntegerField(default=-1)
    content_formatters = models.CharField(max_length=5096, default="")
    content_callback = models.CharField(max_length=5096, default="")

    is_sent = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)

    group_name = models.CharField(max_length=5096, default="")

# LOCALIZATION
class TextString(models.Model): #TODO make connection with outside dictionary

    screen_id = models.CharField(max_length=5096, default="")
    position_index = models.IntegerField(default=-1)

    language_1 = models.CharField(max_length=5096, blank=True)
    language_2 = models.CharField(max_length=5096, blank=True)
    language_3 = models.CharField(max_length=5096, blank=True)
    language_4 = models.CharField(max_length=5096, blank=True)
    language_5 = models.CharField(max_length=5096, blank=True)

class TextLanguage(models.Model):

    self_name = models.CharField(max_length=5096, default="")
