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

class User(models.Model):

    tg_id = models.CharField(max_length=512, blank=True)
    language_code = models.CharField(max_length=512, default="uk")

    password_id = models.IntegerField(default=-1)
    is_logged_in = models.BooleanField(default=False)

    current_screen_code = models.CharField(max_length=512, default="uk")
    screen_messages_ids = models.CharField(max_length=512, default="")
    remainders_ids = models.CharField(max_length=512, default="")

    @classmethod
    def _get_(cls, user_id):

        for user in cls.objects.all():
            if user.id == user_id:
                return user

    def _update_screen_(self, new_screen_id):
        
        self.current_screen_code = new_screen_id

        for message_id in eval(self.screen_messages_ids):
            try:
                FeedBot.deep[0].delete_message(self.tg_id, message_id)
            except:
                pass
            self.screen_messages_ids.pop(f"{message_id};")

        self.save()

    def check_authorization(self):
        return self.is_logged_in

    def demand_authorization(self):
        self.show_screen_to("00")

    def receive_text_from(self, text):
        
        if not self.check_authorization() and self.current_screen_code != "00" and self.current_screen_code != "01":
            self.demand_authorization()
            return         

        screen = Screen._get_(id=self.current_screen_code)
        screen.text(text, self)

    def receive_button_press_from(self, button_id, params):
        if not self.check_authorization() and self.current_screen_code != "00" and self.current_screen_code != "01":
            self.demand_authorization()
            return   

        screen = Screen._get_(id=self.current_screen_code)
        getattr(screen, f"button_{button_id}")(params, self)

    def show_screen_to(self, screen_id):

        self._update_screen_(screen_id)
        screen = Screen._get_(id=screen_id)

        FeedBot.deep[0].send(self, screen)

    def send_remainder_to(self, remainder_id):
        
        self.remainders_ids += f"{remainder_id};"
        self.save()

        remainder = Remainder._get_(id=remainder_id)
        FeedBot.deep[0].send(self, remainder)

class String(models.Model):

    screen_id = models.CharField(max_length=512, default="")
    position_index = models.IntegerField(default=-1)

    uk = models.CharField(max_length=512, blank=True)
    en = models.CharField(max_length=512, blank=True)