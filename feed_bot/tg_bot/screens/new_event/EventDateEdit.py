#import datetime
#import time

from ...bin.utils import Utils
from ..Screen import Screen


class EventDateEdit(Screen):

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "24", "EventDateEdit", bot_strings)

    def text(self, text, user_id):
        
        digits = text.split("-")

        if len(digits) == 3:
            
            try:
                day = int(digits[0])
                month = int(digits[1])
                year = int(digits[2])
                
            except Exception as e:
                return Utils.api("execute_method", 
                model="BotUser",
                params={"id": user_id},
                method={"name": "show_screen_to", "params": ["28", [], ]} #TODO move static formatters into screen class?
                )[0]
                
            event_id = Utils.api("get",
            model="Event",
            params={"admin_id": user_id, "status": 0},
            fields=["id"], 
            )[0][0]

            Utils.api("execute_method",
            model="Event",
            params={"id": event_id},
            method={"name": "update_template", "params": ["date_scheduled", text]},
            )

            return Utils.api("execute_method",
            model="Event",
            params={"id": event_id},
            method={"name": "show_template", "params": []}
            )[0]

        else:
            return Utils.api("execute_method", 
                    model="BotUser",
                    params={"id": user_id},
                    method={"name": "show_screen_to", "params": ["28", [], ]} #TODO move static formatters into screen class?
                    )[0]