# TODO update from pooling to webhook (look https://pythondigest.ru/view/23089/ for an example)

from turtle import pen
from decouple import config

import telebot
import multiprocess as mp

import time

from .utils import Utils

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

    def _add_(self):
        pass

    def _delete_(self):
        pass

    def __init__(self, parent) -> None:
        self.parent = parent

    def run(self):
        pass

class PollingConnection(Connection):
    
    def __repr__(self) -> str:
        return "Polling"

    def _input_(self, message):
        
        if type(message) == telebot.types.Message and not message.text.startswith("/"):
            mess_id =  message.message_id
            mess_type = "text"
            mess_content = message.text
        elif type(message) == telebot.types.Message and message.text.startswith("/"):
            mess_id =  message.message_id
            mess_type = "command"
            mess_content = message.text
        elif type(message) == telebot.types.CallbackQuery:
            mess_id =  message.id
            mess_type = "button"
            mess_content = [message.data, message.message.message_id]

        else: # TODO think about adding support for other types
            mess_id = -1
            mess_type = "other"
            mess_content = "n\\a"

        message_data = {"user_id": str(message.from_user.id), "mess_id": mess_id, "mess_type": mess_type, "mess_content": mess_content}

        self.parent.receive(message_data)

    def _output_(self, to, what):  
        
        text_to_send = what[0].replace("\\n", "\n") # \n does not work for strings received from the db
        
        mess = self.parent.send_message(to, text_to_send, reply_markup=what[1])
        return mess.message_id

    def _add_(self, user_id, array_name, screen_id, message_id):

        data_raw = Utils.api("get",
        model="BotUser",
        params={"id": user_id},
        fields=[array_name,]
        )[0][0]

        data = eval(data_raw)

        if screen_id not in list(data.keys()):
            data[screen_id] = list()

        data[screen_id].append(message_id)

        Utils.api("update", 
        model="BotUser",
        filter_params={"id": user_id},
        update_params={array_name: str(data)}
        )

    def _delete_(self, user_id, array_name, filter):
        
        tg_id, data_raw = Utils.api("get",
        model="BotUser",
        params={"id": user_id},
        fields=["tg_id", array_name]
        )[0]

        data = eval(data_raw)

        messages_ids = []
        for k, val in data.items():
            for i, v in enumerate(val):
                if eval(filter):
                    messages_ids.append(data[k][i])

        for message_id in messages_ids:
            try:
                for k, val in data.copy().items():
                    if message_id in val:
                        data[k].remove(message_id)
                self.parent.delete_message(tg_id, int(message_id))
            except Exception as e:
                pass
                #print(e)

        Utils.api("update", 
        model="BotUser",
        filter_params={"id": user_id},
        update_params={array_name: str(data)}
        )

    def run_schedule(self, parent): #TODO make schedule as separate "driver"

        Utils.init_screens("bot") #TODO fix

        while True:

            scheduled_messages = Utils.api("get",
            model="ScheduledMessage",
            params={"is_sent": 0, "is_active": 1},
            fields=["id", "user_id", "epoch", "content_type", "content_id", "content_formatters", "content_callback"]
            )

            if type(scheduled_messages) is list and len(scheduled_messages) > 0 and scheduled_messages[0] != 0:
                for scheduled_message in scheduled_messages:

                    if int(scheduled_message[2]) <= int(time.time()):

                        tg_id = Utils.api("get", 
                        model="BotUser",
                        params={"id": scheduled_message[1]},
                        fields=["tg_id",])[0][0]

                        Utils.api("update",
                        model="ScheduledMessage",
                        filter_params={"id": scheduled_message[0]},
                        update_params={"is_sent": 1}
                        )

                        parent.process_received({"user_id": tg_id}, [[str(scheduled_message[4]), "scheduled", eval(scheduled_message[5]), eval(scheduled_message[6]), scheduled_message[0]], ])

            time.sleep(int(config("telebot_scheduled_messages_update_interval"))) #TODO add outside control - instead of sleeping the whole time, sleep 1 second and check flags in "parent" (run now / pause)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        
        @self.parent.message_handler(func=lambda message: True)
        @self.parent.callback_query_handler(func=lambda message: True)
        def handler(message):
            self._input_(message)

    def run(self):

        scheduling = mp.Process(target=self.run_schedule, name="scheduling", args=(self.parent, ))
        scheduling.start()

        self.parent.infinity_polling()

class WebHookConnection(Connection):
    
    def __repr__(self) -> str:
        return "Web hook"

    def _input_(self):
        raise NotImplemented("Web hook connection option is not written yet!")

    def _output_(self):
        raise NotImplemented("Web hook connection option is not written yet!")

    def _add_(self):
        raise NotImplemented("Web hook connection option is not written yet!")

    def _delete_(self):
        raise NotImplemented("Web hook connection option is not written yet!")

    def __init__(self, parent) -> None:
        raise NotImplemented("Web hook connection option is not written yet!")

    def run(self):
        raise NotImplemented("Web hook connection option is not written yet!")
        