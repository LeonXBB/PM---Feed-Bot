from re import L
from telebot import TeleBot
from decouple import config

from feed_bot.tg_bot.models import User

from .connections import Connection


class FeedBot(TeleBot):

    deep = []

    def __init__(self) -> None:
        
        super().__init__(config("telebot_token"))        
        self.connection = Connection.install(config("telebot_connection_type"), self)
        self.deep.append(self)

    def run(self):
        print(f"Feed Bot running with connection {str(self.connection)}")
        self.connection.run()

    def send(self, message):
        self.connection.output(message.show())

    def receive(self, message):
        
        user = User._get_(message["user_id"])

        if message["mess_type"] == "text":
            user.receive_text_from(message["mess_content"])
        else:
            split_content = message["mess_content"].split("_")
            button_id = split_content[0]
            params = split_content[1:]
            user.receive_button_press_from(self, button_id, params)

        self.delete_message(message["user_id"], message["mess_id"])


            