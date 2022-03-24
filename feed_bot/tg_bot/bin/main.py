from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from decouple import config

from .connections import Connection
from .utils import Utils
from ..screens.Screen import Screen
from ..screens.remainders.Remainder import Remainder

class FeedBot(TeleBot):

    def __init__(self) -> None:
        
        super().__init__(config("telebot_token"), parse_mode=config("telebot_parse_mode"))        
        self.connection = Connection.install(config("telebot_connection_type"), self)

    def run(self):

        Utils.init_screens("bot")
        Utils.api("kick_in")

        print(f"Feed Bot running with connection {str(self.connection)}") #TODO change to logger
        self.connection.run()

    def send(self, data): # _user_id_, id(text, keyboard), __type__, formatters
    
        obj = None
        if data[2] == "screen":
            obj = Screen._get_(id=data[1])        
        elif data[2] == "scheduled":
            obj = Remainder._get_(screen_id=data[1])        

        print(data, obj)

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
                        
                        button_formatter = data[3][messages_count + len(keyboards)][i] if data[3] is not None and len(data[3]) > messages_count + len(keyboards) and data[3][messages_count + len(keyboards)] is not None and len(data[3][messages_count + len(keyboards)]) > i else list()
                        
                        print(button)
                        keyboard[-1].append(InlineKeyboardButton(button["text"][user_language_id].format(button_formatter), callback_data=button["data"]))
                        i += 1
                    
                keyboards.append(InlineKeyboardMarkup(keyboard))

        rv = []

        for i in range(messages_count):
           
            text_dict_index = obj.strings[i]
            text = text_dict_index[0][user_language_id]
            texts.append(text)

            formatters = data[3][i] if type(data[3]) is list and len(data[3]) > i and data[3][i] is not None else list() 
            text = texts[i].format(*formatters)
            keyboard = None if len (keyboards) <= i else keyboards[i]

            rv.append(self.connection._output_(user_tg_id, (text, keyboard)))

        return rv

    def receive(self, message):
        
        user_id, user_language_id, user_current_screen_code = Utils.api("get_or_make", 
            model="BotUser", 
            fields=["id", "language_id", "current_screen_code"],
            params={"tg_id": message["user_id"]},
        )[0]

        reply = None

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
            
            split_content = message["mess_content"].split("_")
            button_id = split_content[0]
            params = split_content[1:]
            
            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_button_press_from", "params": [button_id, params]}
            )

        elif message["mess_type"] == "button" and message["mess_content"].startswith("r"):
            
            split_content = message["mess_content"].split("_")
            button_id = split_content[1]
            remainder_id = split_content[2]
            params = split_content[3:]
              
            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_button_press_from", "params": [button_id, params]}
            )        
        
        if message["mess_type"] != "button": 
            self.connection._add_(user_id, "user_input_messages_ids", str(user_current_screen_code), message["mess_id"])
            self.connection._delete_(user_id, "user_input_messages_ids", f"k == {(user_current_screen_code)}")

        if reply is not None and hasattr(reply, "__len__") and len(reply) > 0 and reply[0] is not None:

            self.process_received(message, reply)

    def process_received(self, message, reply):

        user_id, user_language_id, user_current_screen_code = Utils.api("get", 
            model="BotUser", 
            fields=["id", "language_id", "current_screen_code"],
            params={"tg_id": message["user_id"]}
        )[0]

        if type(reply) is list and len(reply) > 0 and type(reply[0]) is list and len(reply[0]) > 0 and type(reply[0][0]) is list:
            reply = reply[0] # TODO fix this hack for when we have remainders, as api.execute_method adds its own list 

        for screen_data in reply:

            if screen_data[1] != "remainder":

                # show next screen
                screen_data.insert(0, [message["user_id"], user_language_id])
                new_messages_ids = self.send(screen_data)

                if screen_data[2] == "screen":

                    # delete previous screen
                    self.connection._delete_(user_id, "screen_messages_ids", f"k != {user_current_screen_code}")

                    # add current screen to user field
                    for new_message_id in new_messages_ids:
                        self.connection._add_(user_id, "screen_messages_ids", str(user_current_screen_code), new_message_id)
                    
                elif screen_data[2] == "scheduled":
                    
                    for new_message_id in new_messages_ids:
                        self.connection._add_(user_id, "remainders_ids", screen_data[1], new_message_id)

            else:
                
                Utils.api("get_or_make",
                model="ScheduledMessage",
                params={"user_id": user_id, "epoch": screen_data[2], "content_type": "Remainder", "content_id": screen_data[0], "content_formatters": screen_data[3], "is_sent": 0},
                fields=[]
                )