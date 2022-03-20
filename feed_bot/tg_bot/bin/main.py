from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from decouple import config

from .connections import Connection
from .utils import Utils
from ..screens.Screen import Screen
from ..screens.remainders.Remainder import Remainder

class FeedBot(TeleBot):

    def __init__(self) -> None:
        
        super().__init__(config("telebot_token"))        
        self.connection = Connection.install(config("telebot_connection_type"), self)

    def run(self):

        Utils.init_screens("bot")
        Utils.api("kick_in")

        print(f"Feed Bot running with connection {str(self.connection)}") #TODO change to logger
        self.connection.run()

    def send(self, data): # _user_id_, id(text, keyboard), __type__, formatters
    
        if data[2] == "screen":
            obj = Screen._get_(id=data[1])        
        elif data[2] == "remainder":
            obj = Remainder._get_(id=data[1])        

        user_tg_id = data[0][0]
        user_language_id = data[0][1]
        
        messages_count = len(list(obj.strings.keys())) - len(obj.keyboards)
        texts = []
        
        layouts = obj.keyboards
        keyboards = []

        for layout in layouts:
            if layout is not None:
                keyboard = []
                i = 0
                for row in layout:
                    keyboard.append(list())
                    for button in row:
                        button_formatter = data[3][messages_count + len(keyboards)][i] if data[3] is not None and len(data[3]) > messages_count + len(keyboards) and data[3][messages_count + len(keyboards)] is not None else list()
                        print(button_formatter)
                        keyboard[-1].append(InlineKeyboardButton(button["text"][user_language_id].format(button_formatter), callback_data=button["data"]))
                        i += 1
                    
                keyboards.append(InlineKeyboardMarkup(keyboard))

        rv = []

        for i in range(messages_count):
           
            text_dict_index = obj.strings[i]
            text = text_dict_index[0][user_language_id]
            texts.append(text)

            formatters = data[3][i] if data[3] is not None and data[3][i] is not None else list()
            text = texts[i].format(*formatters)
            keyboard = None if len (keyboards) <= i else keyboards[i]

            rv.append(self.connection._output_(user_tg_id, (text, keyboard)))

        return rv

    def receive(self, message):
        
        user_id, user_language_id = Utils.api("get_or_make", 
            model="BotUser", 
            fields=["id", "language_id"],
            params={"tg_id": message["user_id"]}
        )[0]

        if message["mess_type"] == "text":
            
            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_text_from", "params": [message["mess_content"], ]}
            )

        elif message["mess_type"] == "command":
            
            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_command_from", "params": [message["mess_content"], ]}
            )

        elif message["mess_type"] == "button" and not message["mess_content"].startswith("r"):
            
            reply = split_content = message["mess_content"].split("_")
            button_id = split_content[0]
            params = split_content[1:]
            
            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_button_press_from", "params": [button_id, params]}
            )

        elif message["mess_type"] == "button" and message["mess_content"].startswith("r"):
            
            pass # TODO write code for remainders, including deletion       

        user_id, user_language_id = Utils.api("get", 
            model="BotUser", 
            fields=["id", "language_id"],
            params={"tg_id": message["user_id"]}
        )[0] # in case user has chainged their language. Or id...
     
        # TODO move delete function to connections (possibly, connect with output?)
        if message["mess_type"] != "button": 
            try:
                self.delete_message(message["user_id"], message["mess_id"])
            except:
                pass 
        
        # delete previous screen

        previous_messages = Utils.api("get",
        model="BotUser",
        params={"id": user_id},
        fields=["screen_messages_ids",]
        )[0][0]

        previous_messages = previous_messages.split(";")
        for message_id in previous_messages:
            if message_id:
                try:
                    self.delete_message(message["user_id"], int(message_id))
                except Exception as e: 
                    print(e)

        # show next screen

        for i, screen_data in enumerate(reply): # TODO wrong for loop
            screen_data.insert(0, [message["user_id"], user_language_id])
            new_messages_ids = self.send(screen_data)

        # add current screen to user field

            if screen_data[2] == "screen":
                Utils.api("update",
                model="BotUser",
                filter_params={"id": user_id},
                update_params={"screen_messages_ids": f'{";".join(str(x) for x in new_messages_ids)};'}
                )

            elif screen_data[2] == "remainder":
                Utils.api("update",
                model="BotUser",
                filter_params={"id": user_id},
                update_params={"remainders_ids": f'{";".join(str(x) for x in new_messages_ids)};'}
                )
