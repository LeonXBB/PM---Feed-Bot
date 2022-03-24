from decouple import config

from django.db import models

import hashlib
import time

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

    created = models.CharField(max_length=512, default=";") # user_id, timestamp
    status = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def _cancel_(self):
        self.status ="Cancelled"

class Event(LogicModel):  #TODO move template to different class?
    
    # statuses: 0 - being created, 1 - awaiting start, 2 - ongoing, 3 - between periods, 4 - finished, 5 - cancelled 
    
    admin_id = models.IntegerField(default=-1)

    competition_id = models.IntegerField(default=-1)
    rules_set_id = models.IntegerField(default=-1)

    date_scheduled =  models.CharField(max_length=5096, default="")
    time_scheduled = models.CharField(max_length=5096, default="")
    date_actual = models.CharField(max_length=5096, default="")
    time_actual = models.CharField(max_length=5096, default="")

    home_team_id = models.IntegerField(default=-1)
    away_team_id = models.IntegerField(default=-1)

    periods_ids = models.CharField(max_length=5096, default=";")
    coin_toss_ids = models.CharField(max_length=5096, default=";")
    timer_ids = models.CharField(max_length=5096, default=";")

    def make_template(self):
        pass

    def show_template(self): 

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

    def edit_template(self):
        pass

    def save_template(self):
        pass

    def start(self):
        pass

    def end(self):
        pass

    def run(self):
        pass

    def cancel(self):
        self._cancel_()
        pass

class Team(LogicModel):
    
    name = models.CharField(max_length=512, default="")
    events_ids = models.CharField(max_length=512, default=";") 

class Competition(LogicModel): #TODO MOVE FROM DEFAULT DATABASE TO LOGIC (flush dbs?)

    name = models.CharField(max_length=512, default="")
    events_ids = models.CharField(max_length=512, default=";")

class RulesSet(LogicModel):
    
    name = models.CharField(max_length=512, default="")

    win_event_by = models.IntegerField(default=0)
    win_period_by = models.CharField(max_length=512, default=';')

    periods_in_event = models.IntegerField(default=2)
    periods_to_win_event = models.IntegerField(default=2)

    points_in_period = models.IntegerField(default=2)
    points_to_win_period = models.CharField(max_length=512, default=';')

    stop_event_after_enough_periods = models.BooleanField(default=False)
    stop_period_after_enough_points = models.BooleanField(default=False)

    min_difference_periods_to_win_event = models.IntegerField(default=0)
    min_difference_points_to_win_period = models.CharField(max_length=512, default=';')

    points_per_score_per_period = models.CharField(max_length=512, default=';')
    scores_names = models.CharField(max_length=512, default=';')

    event_length_minutes = models.IntegerField(default=0)
    periods_lenght_minutes = models.CharField(max_length=512, default=';')

    interval_between_periods_munutes = models.CharField(max_length=512, default=';')

    event_timer_direction = models.IntegerField(default=0)
    period_timers_directions = models.CharField(max_length=512, default=';')

    event_timer_stops_at_pauses = models.BooleanField(default=False)
    period_timers_stop_at_pauses = models.CharField(max_length=512, default=';')

    side_changes_after_periods = models.CharField(max_length=512, default=';')
    side_changes_during_periods = models.CharField(max_length=512, default=';')
    side_changes_during_periods_scores = models.CharField(max_length=512, default=';')
    side_changes_during_periods_pause_time_seconds = models.CharField(max_length=512, default=';')
    
    coin_tosses_before_periods = models.CharField(max_length=512, default=';')
    coin_toss_start_before_minutes  = models.CharField(max_length=512, default=';')

    time_outs_per_team_per_period = models.CharField(max_length=512, default=';')
    time_outs_lenghts_per_team_per_period = models.CharField(max_length=512, default=';')
    
    technical_time_outs_lenghts_per_period = models.CharField(max_length=512, default=';')
    technical_time_outs_at_score_per_period = models.CharField(max_length=512, default=';')
    
    actions_list = models.CharField(max_length=512, default=';')
    
    event_start_remainder_minutes_before = models.CharField(max_length=512, default=';')
    event_end_remainder_minutes_before = models.CharField(max_length=512, default=';')
    period_start_remainder_minutes_before = models.CharField(max_length=512, default=';')
    period_end_remainder_minutes_before = models.CharField(max_length=512, default=';')
    coin_toss_remainder_minutes_before = models.CharField(max_length=512, default=';')
    
    def register(self):
        pass

    def delete(self):
        pass

# TELEBOT
class PasswordPair(models.Model):
    
    password_sha256 = models.CharField(max_length=512)
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

    tg_id = models.CharField(max_length=512, blank=True)
    language_id = models.IntegerField(default=0)

    password_id = models.IntegerField(default=-1)
    is_logged_in = models.IntegerField(default=0)
    is_superadmin = models.IntegerField(default=0)

    current_screen_code = models.CharField(max_length=512, default="00")

    screen_messages_ids = models.CharField(max_length=512, default=f"{{}}")
    remainders_ids = models.CharField(max_length=512, default=f"{{}}")
    user_input_messages_ids = models.CharField(max_length=512, default=f"{{}}")

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

    def receive_button_press_from(self, button_id, params, remainder_id=None, message_id=None):
        if not self.check_authorization():
            return self.show_screen_to("00")       
        
        if remainder_id is None:
            
            screen = Screen._get_(id=self.current_screen_code)
            return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id)

        elif remainder_id is not None:

            screen = Remainder._get_(remainder_id=remainder_id)
            return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id, message_id)

    def show_screen_to(self, screen_id, format_strs=None):
        self.current_screen_code = screen_id
        self.save()
        return [screen_id, "screen", format_strs]

    def send_remainder_to(self, remainder_id, epoch, format_strs=None):
        return [remainder_id, "remainder", epoch, format_strs]

class ScheduledMessage(models.Model):

    user_id = models.IntegerField(default=-1)

    epoch = models.CharField(max_length=512, default="")

    content_type = models.CharField(max_length=512, default="remainder")
    content_id = models.IntegerField(default=-1)
    content_formatters = models.CharField(max_length=512, default="")

    is_sent = models.IntegerField(default=0)

# LOCALIZATION
class TextString(models.Model): #TODO make connection with outside dictionary

    screen_id = models.CharField(max_length=512, default="")
    position_index = models.IntegerField(default=-1)

    language_1 = models.CharField(max_length=512, blank=True)
    language_2 = models.CharField(max_length=512, blank=True)
    language_3 = models.CharField(max_length=512, blank=True)
    language_4 = models.CharField(max_length=512, blank=True)
    language_5 = models.CharField(max_length=512, blank=True)

class TextLanguage(models.Model):

    self_name = models.CharField(max_length=512, default="")
