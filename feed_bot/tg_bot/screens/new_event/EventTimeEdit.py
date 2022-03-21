from ...bin.utils import Utils
from ..Screen import Screen


class EventTimeEdit(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "25", "EventTimeEdit")

    def text(self, text, user_id):
        
        digits = text.split(":")

        if len(digits) == 2:
            for digit in digits:
                try:
                    int(digit) #TODO change to epoch
                except:
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

            Utils.api("update", 
            model="Event",
            filter_params={"id": event_id},
            update_params={"delete_time": text}        
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