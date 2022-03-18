# TODO update from pooling to webhook (look https://pythondigest.ru/view/23089/ for an example)

from decouple import config
import telebot

import requests

from . import utils

class Connection:

    def __repr__(self) -> str:
        return "default (you shouldn't be using it!)"

    @classmethod
    def install(cls, type, parent):
        
        cls.connections = {
            "default": cls,
            "polling": PollingConnection,
            "web_hook": WebHookConnection
        }

        return cls.connections.get(type, None)(parent)

    def _input_(self):
        pass

    def _output_(self):
        pass

    def __init__(self, parent) -> None:
        self.parent = parent

    def run(self):
        pass

class PollingConnection(Connection):
    
    def __repr__(self) -> str:
        return "Polling"

    def _input_(self, message):
        
        if type(message) == telebot.types.Message:
            mess_type = "text"
            mess_content = message.text
        elif type(message) == telebot.types.InlineQuery:
            mess_type = "button"
            mess_content = message.data
        else: # TODO add support for other types
            mess_type = "other"
            mess_content = "n\\a"

        message_data = {"user_id": message.from_user.id, "mess_id": message.message_id, "mess_type": mess_type, "mess_content": mess_content}

        self.parent.receive(message_data)

    def _output_(self, to, message):

        messages = []

        for i, separate_message in enumerate(message):
            messages.append(dict())
            messages[-1]["text"] = separate_message[0]
            messages[-1]["text"] = separate_message[1]
        
        for message_ in messages:
            self.parent.send_message(to, message_[0], reply_markup=message_[1])    

    def __init__(self, parent) -> None:
        super().__init__(parent)
        
        @self.parent.message_handler(func=lambda message: True)
        def handler(message):
            json_dict={"task": "update", "id": message.from_user.id, "text": message.text}
            requests.post(config("server_address"), data=json_dict)
            requests.post(f"{config('server_address')}new_ind", data=json_dict)
            self._input_(message)

    def run(self):
        self.parent.infinity_polling()


class WebHookConnection(Connection):
    
    def __repr__(self) -> str:
        return "Web hook"

    def _input_(self):
        raise NotImplemented("Web hook connection option is not written yet!")

    def _output_(self):
        raise NotImplemented("Web hook connection option is not written yet!")

    def __init__(self, parent) -> None:
        raise NotImplemented("Web hook connection option is not written yet!")

    def run(self):
        raise NotImplemented("Web hook connection option is not written yet!")
        