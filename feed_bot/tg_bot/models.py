from decouple import config

import hashlib
from django.db import models

from .screens.Screen import Screen
from .screens.remainders.Remainder import Remainder

# Create your models here.

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

    current_screen_code = models.CharField(max_length=512, default="uk")
    screen_messages_ids = models.CharField(max_length=512, default=";")
    remainders_ids = models.CharField(max_length=512, default=";")

    def check_authorization(self, ignore_authorization_screens=False):
        return self.is_logged_in or ((self.current_screen_code == "00" or self.current_screen_code == "01") and ignore_authorization_screens)

    def receive_text_from(self, text):
        
        if not self.check_authorization(True):
            return self.show_screen_to("00")       

        screen = Screen._get_(id=self.current_screen_code)
            
        return screen.text(text, self.id)

    def receive_command_from(self, command):
        if not self.check_authorization():
            return self.show_screen_to("00")       

        if command == "/start":
            return self.show_screen_to("10", [[config("telebot_version")], ]) #TODO move static formatters into screen class?
        elif command.startswirh('/show screen'):
            if self.is_superadmin:
                return self.show_screen_to(*command.split(" ")[2:])
        else:    
            return self.receive_text_from(command)

    def receive_button_press_from(self, button_id, params):
        if not self.check_authorization():
            return self.show_screen_to("00")       
               
        screen = Screen._get_(id=self.current_screen_code)
        return getattr(screen, f"button_{button_id}")(params, self.id)

    def show_screen_to(self, screen_id, format_strs=None):
        self.current_screen_code = screen_id
        self.save()
        return [screen_id, "screen", format_strs]

    def send_remainder_to(self, remainder_id, format_strs=None):
        return [remainder_id, "remainder", format_strs]

class TextString(models.Model):

    screen_id = models.CharField(max_length=512, default="")
    position_index = models.IntegerField(default=-1)

    language_1 = models.CharField(max_length=512, blank=True)
    language_2 = models.CharField(max_length=512, blank=True)
    language_3 = models.CharField(max_length=512, blank=True)
    language_4 = models.CharField(max_length=512, blank=True)
    language_5 = models.CharField(max_length=512, blank=True)

class TextLanguage(models.Model):

    self_name = models.CharField(max_length=512, default="")
