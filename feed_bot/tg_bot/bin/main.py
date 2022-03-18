from telebot import TeleBot
from decouple import config

import requests

from .connections import Connection


class FeedBot(TeleBot):

    def __init__(self) -> None:
        
        super().__init__(config("telebot_token"))        
        self.connection = Connection.install(config("telebot_connection_type"), self)

    def run(self):

        from ..screens import all_screens

        for screen in all_screens:
            screen()

        print(f"Feed Bot running with connection {str(self.connection)}")
        self.connection.run()

    def send(self, data, language_id):
        
        from ..screens.Screen import Screen
        from ..screens.remainders.Remainder import Remainder

        if data[2] == "screen":
            obj = Screen._get_(id=data[1])        
        elif data[2] == "remainder":
            obj = Remainder._get_(id=data[1])        

        obj_data = obj.show()

        print(language_id)
        print(obj_data[0])

        self.connection._output_(data[0], (obj_data[0][language_id], obj_data[1], *data[2:4]))

    def receive(self, message):
        
        user_getter = requests.post(f"{config('server_address')}/api", json={"task": "get_or_make", "class": "BotUser", "fields": ["id", "language_id"], "params": {"tg_id": message["user_id"]}})
        user_id = user_getter.json()[0][0]
        user_language_id = user_getter.json()[0][1]

        if message["mess_type"] == "text":
            reply = requests.post(f"{config('server_address')}/api", json={"task": "execute_method", "class": "BotUser", "fields": ["id"], "params": {"id": user_id}, "method": {"name": "receive_text_from", "params": [message["mess_content"], ]}})
        elif message["mess_type"] == "command":
            reply = requests.post(f"{config('server_address')}/api", json={"task": "execute_method", "class": "BotUser", "fields": ["id"], "params": {"id": user_id}, "method": {"name": "receive_command_from", "params": [message["mess_content"], ]}})        
        elif message["mess_type"] == "button":
            reply = split_content = message["mess_content"].split("_")
            button_id = split_content[0]
            params = split_content[1:]
            requests.post(f"{config('server_address')}/api", json={"task": "execute_method", "class": "BotUser", "params": {"id": user_id}, "method": {"name": "receive_button_press_from", "params": [button_id, params]}})

        self.delete_message(message["user_id"], message["mess_id"]) # TODO move delete function to connections (possibly, connect with output?)

        for piece in reply.json():
            piece.insert(0, message["user_id"])
            self.send(piece, user_language_id)