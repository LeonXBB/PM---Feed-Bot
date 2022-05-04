from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from decouple import config

import time

from .connections import Connection
from .utils import Utils
from ..screens.Screen import Screen
from ..screens.remainders.Remainder import Remainder

class FeedBot(TeleBot):

    def __init__(self) -> None:
        
        super().__init__(config("telebot_token"), parse_mode=config("telebot_parse_mode"))        
        self.connection = Connection.install(config("telebot_connection_type"), self)

    def run(self):

        print("\n", time.strftime("%H:%M:%S"), "Starting the server...\n")
        Utils.api("kick_in")
        print(time.strftime("%H:%M:%S"), "Server started.\n")
        print(time.strftime("%H:%M:%S"), "Starting screens init for the bot...\n")
        Utils.init_screens("bot")
        print("\n", time.strftime("%H:%M:%S"), "Screens init for the bot finished.\n")

        print(time.strftime("%H:%M:%S"), f"Feed Bot running with connection {str(self.connection)}\n") #TODO change to logger
        self.connection.run()

    def send(self, data): # user(tg_id, language_id), id(text, keyboard), __type__, formatters, dynamic button_values
       
        print(time.strftime("%H:%M:%S"), "Calculating obj reference...")
        obj = None
        if data[2] == "screen":
            obj = Screen._get_(id=data[1])        
        elif data[2] == "scheduled":
            obj = Remainder._get_(screen_id=data[1])        

        user_tg_id = data[0][0]
        user_language_id = data[0][1]
        
        print(time.strftime("%H:%M:%S"), "Obj reference сalculated. Getting messages count...")
        messages_count = len(list(obj.strings.keys() if hasattr(obj, "strings") else obj.get_strings(data))) - len(obj.keyboards if hasattr(obj, "keyboards") else obj.get_keyboards(data))

        print(time.strftime("%H:%M:%S"), "Messages count got. Parsing keyboard(s)...")

        texts = []

        layouts = obj.keyboards if hasattr(obj, "keyboards") else obj.get_keyboards(data)
        keyboards = []

        for layout in layouts:
            if layout is not None:
                keyboard = []
                i = 0
                for row in layout:
                    keyboard.append(list())
                    for button in row:
                        
                        button_formatter = data[3][messages_count + len(keyboards)][i] if data[3] is not None and len(data[3]) > messages_count + len(keyboards) and data[3][messages_count + len(keyboards)] is not None and len(data[3][messages_count + len(keyboards)]) > i else list()
                        callback_formatter = data[4][len(keyboards) - 1][i] if data[4] is not None and len(data[4]) >= len(keyboards) and data[4][len(keyboards)] is not None and len(data[4][len(keyboards)]) > i else list()
                        
                        keyboard[-1].append(InlineKeyboardButton(button["text"][user_language_id].format(button_formatter), callback_data=button["data"].format(callback_formatter)))
                        i += 1
                    
                keyboards.append(InlineKeyboardMarkup(keyboard))

        rv = []

        print(time.strftime("%H:%M:%S"), "Keyboard(s) parsed. Parsing text strings...")

        for i in range(messages_count):
           
            text_dict_index = obj.strings[i] if hasattr(obj, "strings") else obj.get_strings(data)[i]
            text = text_dict_index[0][user_language_id]
            texts.append(text)

            print(time.strftime("%H:%M:%S"), f"Text strings for message {i} parsed. Parsing formatters...")

            formatters = data[3][i] if type(data[3]) is list and len(data[3]) > i and data[3][i] is not None else list() 
            text = texts[i].format(*formatters)
            keyboard = None if len (keyboards) <= i else keyboards[i]

            print(time.strftime("%H:%M:%S"), f"Formatters for message {i} parsed. Sending message...")

            rv.append(self.connection._output_(user_tg_id, (text, keyboard)))

        return rv

    def receive(self, message):
        
        print("\n", time.strftime("%H:%M:%S"), "Received message from user. Getting their info...")

        user_id, user_language_id, user_current_screen_code = Utils.api("get_or_make", 
            model="BotUser", 
            fields=["id", "language_id", "current_screen_code"],
            params={"tg_id": message["user_id"]},
        )[0]

        print(time.strftime("%H:%M:%S"), "Got user info. Calculating reply...")

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

        elif message["mess_type"] == "button" and not message["mess_content"][0].startswith("r_") and not message["mess_content"][0].startswith("d_"):
            
            self.answer_callback_query(message["mess_id"])

            split_content = message["mess_content"][0].split("_")
            button_id = split_content[0]
            params = split_content[1:]
            
            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_button_press_from", "params": [button_id, params, "screen"]}
            )

        elif message["mess_type"] == "button" and message["mess_content"][0].startswith("r_"):
            
            self.answer_callback_query(message["mess_id"])

            split_content = message["mess_content"][0].split("_")
            button_id = split_content[1] # number
            remainder_id = split_content[2]
            message_id = message["mess_content"][1] # tg bot message
            params = split_content[3:]
            
            scheduled_messages = Utils.api("get_all",
            model="ScheduledMessage",
            fields=["id", "messages_ids"])

            for scheduled_message in scheduled_messages:
                for bot_message_id in scheduled_message[1].split(";"):
                    if bot_message_id:
                        if int(bot_message_id) == int(message_id):
                            scheduled_message_id = scheduled_message[0]

            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_button_press_from", "params": [button_id, params, "remainder", remainder_id, scheduled_message_id]}
            )        
                  
            if len(str(remainder_id)) == 2: remainder_id = f"1{remainder_id}"
            self.connection._delete_(user_id, "remainders_ids", f"str(k) == str({remainder_id}) and int(v) == int({message_id})")

        elif message["mess_type"] == "button" and message["mess_content"][0].startswith("d_"):
            
            self.answer_callback_query(message["mess_id"])

            split_content = message["mess_content"][0].split("_")
            screen_id = split_content[1]
            button_id = split_content[2]
            params = split_content[3:]
            
            reply = Utils.api("execute_method", 
            model="BotUser",
            params={"id": user_id},
            method={"name": "receive_button_press_from", "params": [button_id, params, "screen", screen_id]}
            )

        print(time.strftime("%H:%M:%S"), "Calculated reply to user message.")

        if message["mess_type"] != "button": 
            self.connection._add_(user_id, "user_input_messages_ids", user_current_screen_code, message["mess_id"])
            self.connection._delete_(user_id, "user_input_messages_ids", f"int(k) == int({user_current_screen_code})")

        if reply is not None and hasattr(reply, "__len__") and len(reply) > 0 and reply[0] is not None:
            print(time.strftime("%H:%M:%S"), "Sending reply to user...")
            self.process_received(message, reply)
            print(time.strftime("%H:%M:%S"), "Reply sent.\n")

    def process_received(self, message, reply):

        print(time.strftime("%H:%M:%S"), "Updating user info (if changed in reply)...")

        user_id, user_language_id, = Utils.api("get", 
            model="BotUser", 
            fields=["id", "language_id"],
            params={"tg_id": message["user_id"]}
        )[0]

        print(time.strftime("%H:%M:%S"), "User info updated.")

        if type(reply) is list and len(reply) > 0 and type(reply[0]) is list and len(reply[0]) > 0 and type(reply[0][0]) is list:
            reply = reply[0] # TODO fix this hack for when we have remainders, as api.execute_method adds its own list 

        print(time.strftime("%H:%M:%S"), "Calculating screens to delete / save...")
        screens_ids = []
        ignore_ids = []
        add_ids = []

        if len(reply) > 1 and type(reply[-1][0]) is str and all(type(x) is int for x in reply[-1][1:]):
            eval(f"{reply[-1][0]}_ids.extend({reply[-1][1:]})")
            reply = reply[:-1]

        screens_ids.extend(add_ids)
        for screen_data in reply:
            if int(screen_data[0]) not in ignore_ids: screens_ids.append(screen_data[0])

        print(time.strftime("%H:%M:%S"), "Screens to delete / save calculated. Deleting calculated screens...")
        for i, screen_data in enumerate(reply):
            if screen_data[1] == "screen" and len(reply) > 1:
            
                # delete previous screens for complicated menus
                self.connection._delete_(user_id, "screen_messages_ids", f"str(k) not in {screens_ids}")  
        print(time.strftime("%H:%M:%S"), "Calculated screens deleted.")

        for i, screen_data in enumerate(reply):
            print(time.strftime("%H:%M:%S"), f"Processing screen {i} of {len(reply)}...")
            if screen_data[1] != "remainder":
                print(time.strftime("%H:%M:%S"), "Formatting screen data...")
                # show next screen
                screen_data.insert(0, [message["user_id"], user_language_id])
                print(time.strftime("%H:%M:%S"), "Screen data formatted. Sending screen...")
                new_messages_ids = self.send(screen_data)
                print(time.strftime("%H:%M:%S"), "Screen sent. Updating messages ids...")

                if screen_data[2] == "screen":

                    # delete previous screens
                    if len(reply) == 1: self.connection._delete_(user_id, "screen_messages_ids", f"str(k) not in {screens_ids}")                    

                    # add current screen to user field
                    for new_message_id in new_messages_ids:
                        self.connection._add_(user_id, "screen_messages_ids", screen_data[1], new_message_id)
                    
                elif screen_data[2] == "scheduled":
                    
                    for new_message_id in new_messages_ids:
                        self.connection._add_(user_id, "remainders_ids", screen_data[1], new_message_id)

                    Utils.api("update",
                    model="ScheduledMessage",
                    filter_params={"id": screen_data[5]},
                    update_params={"messages_ids": ";".join(str(x) for x in new_messages_ids)}
                    )

            else:
                print(time.strftime("%H:%M:%S"), "Saving remainder...")
                Utils.api("get_or_make",
                model="ScheduledMessage",
                params={"user_id": user_id, "epoch": screen_data[2], "content_type": "Remainder", "content_id": screen_data[0], "content_formatters": screen_data[3], "is_sent": 0, "is_active": 1, "group_name": screen_data[4], "content_callback": screen_data[5]},
                fields=[]
                )
                print(time.strftime("%H:%M:%S"), "Remainder saved.")

if __name__ == "__main__":
    FeedBot().run()