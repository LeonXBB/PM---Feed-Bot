from ...bin.utils import Utils
from ..Screen import Screen


class EventTimeEdit(Screen):

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "25", "EventTimeEdit", bot_strings)

    def text(self, text, user_id):
        
        digits = text.split(":")

        if len(digits) == 2:
            
            try:
                
                hour = digits[0]
                minute = digits[1]

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
            method={"name": "update_template", "params": ["time_scheduled", text]},
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