from decouple import config

from django.db import models

import time
import hashlib

from ...screens.Screen import Screen
from ...screens.remainders.Remainder import Remainder


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

    blocked_for_new_requests = models.IntegerField(default=0)

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
        
        elif command.startswith('/new_user') and self.is_superadmin:
                
            from .PasswordPair import PasswordPair
            from ...screens.remainders.Remainder import Remainder

            password = command.split("/new_user ")[0]
            new_obj = PasswordPair()

            if len(password) == 64:
                new_obj.password_sha256 = password
            else:
                new_obj.password_sha256 = hashlib.sha256(password.encode('utf-8')).hexdigest()

            new_obj.save()
            
            try:
                return Remainder._get_("PasswordRegistered").schedule(int(time.time()), self.id)
            except Exception as e:
                print(e)

        else:    
            return self.receive_text_from(command)

    def receive_button_press_from(self, button_id, params, screen_type, screen_id="", scheduled_message_id=None):
        
        print(time.strftime("%H:%M:%S"), "Checking authorization status...")
            
        if not self.check_authorization():
            return self.show_screen_to("00")       
        
        print(time.strftime("%H:%M:%S"), "Authorization status checked. Getting reference obj...")

        if screen_type == "screen":
            
            screen = Screen._get_(id=self.current_screen_code if screen_id == "" else str(screen_id))

            print(time.strftime("%H:%M:%S"), "Reference obj obtained. Processing request...")
            
            try:
                return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id)
            except Exception as e:
                print(e)

        elif screen_type == "remainder":

            screen = Remainder._get_(remainder_id=str(screen_id))

            print(time.strftime("%H:%M:%S"), "Reference obj obtained. Processing request...")

            try:
                return None if not hasattr(screen, f"button_{button_id}") else getattr(screen, f"button_{button_id}")(params, self.id, scheduled_message_id)
            except Exception as e:
                print(e)

    def show_screen_to(self, screen_id, format_strs=None, callback_data=None):
        self.current_screen_code = screen_id
        self.save()
        return [screen_id, "screen", format_strs, callback_data]

    def send_remainder_to(self, remainder_id, epoch, format_strs=None, group="", callback_data=None):
        return [remainder_id, "remainder", epoch, format_strs, group, callback_data]

    def show_list_of_events(self, flush_safe=False):

        from ..logic.event.Event import Event

        from ..logic.Team import Team
        from ..logic.Competition import Competition
        from ..logic.RulesSet import RulesSet

        from ..localization.TextString import TextString

        status_strings = []
        for text_string in TextString.objects.all().order_by("id"):
            if text_string.screen_id == "status":
                status_strings.append([text_string.language_1, text_string.language_2, text_string.language_3, text_string.language_4, text_string.language_5])

        rv = []

        for event in Event.objects.all():

            if event.admin_id == self.id: # TODO change to inline if-then (look Event.show_layout)
                
                try:
                    home_team_name = Team._get_({"id": event.home_team_id})[0].name
                except:
                    home_team_name = ""

                try:
                    away_team_name = Team._get_({"id": event.away_team_id})[0].name
                except:
                    away_team_name = ""

                try:
                    competition_name = Competition._get_({"id": event.competition_id})[0].name
                except:
                    competition_name = ""

                try:
                    rules_set_name = RulesSet._get_({"id": event.rules_set_id})[0].name
                except: 
                    rules_set_name = ""

                try:
                    date = event.date_scheduled
                except:
                    date = ""

                try:
                    time_ = event.time_scheduled
                except:
                    time_ = ""

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