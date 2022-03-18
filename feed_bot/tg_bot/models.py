import hashlib

from django.db import models

from .screens.Screen import Screen
from .screens.remainders.Remainder import Remainder
from .bin.main import FeedBot
# Create your models here.

class PasswordPair(models.Model):
    
    pasword_sha256 = models.CharField(max_length=512)
    user_id = models.IntegerField(default=-1)

    def generate(self, string):
        self.pasword_sha256 = hashlib.sha256(string).hexdigest()
        self.save()
    
    def assign_to_user(self, user):
        self.user_id = user.id 
        self.save()

class BotUser(models.Model):

    tg_id = models.CharField(max_length=512, blank=True)
    language_id = models.IntegerField(default=0)

    password_id = models.IntegerField(default=-1)
    is_logged_in = models.BooleanField(default=False)

    current_screen_code = models.CharField(max_length=512, default="uk")
    screen_messages_ids = models.CharField(max_length=512, default="()")
    remainders_ids = models.CharField(max_length=512, default="()")

    def _update_screen_(self, new_screen_id):
        
        self.current_screen_code = new_screen_id

        for message_id in eval(self.screen_messages_ids):
            try:
                FeedBot.deep[0].delete_message(self.tg_id, message_id)
            except:
                pass
            self.screen_messages_ids.pop(f"{message_id},") # TODO process whitespace accordingly when we figure out the sending and saving of messages

        self.save()

    def check_authorization(self, ignore_authorization_screens=False):
        return self.is_logged_in or (self.current_screen_code == "00" and self.current_screen_code == "01" and ignore_authorization_screens)

    def receive_text_from(self, text):
        
        if not self.check_authorization(True):
            return self.show_screen_to("00")       

        screen = Screen._get_(id=self.current_screen_code)
        return screen.text(text, self)

    def receive_command_from(self, command):
        if not self.check_authorization(command == "start"):
            return self.show_screen_to("00")       
             
        return self.receive_text_from(command) # TODO workaround for when we only have once command, change in the future

    def receive_button_press_from(self, button_id, params):
        if not self.check_authorization():
            return self.show_screen_to("00")       
               
        screen = Screen._get_(id=self.current_screen_code)
        return getattr(screen, f"button_{button_id}")(params, self)

    def show_screen_to(self, screen_id, format_strs=None):

        self._update_screen_(screen_id)
        return [screen_id, "screen", format_strs]

    def send_remainder_to(self, remainder_id, format_strs=None):
        
        self.remainders_ids += f"{remainder_id};"
        self.save()

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
