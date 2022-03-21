from ...bin.utils import Utils
from ..Screen import Screen


class WrongFormat(Screen):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "0_0"}

        layout = [(ok, ), ]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "28", "WrongFormat")

    def button_0(self, params, user_id):
        
        event_id = Utils.api("get",
            model="Event",
            params={"admin_id": user_id, "status": 0},
            fields=["id"], 
            )[0][0]
        
        return Utils.api("execute_method",
            model="Event",
            params={"id": event_id},
            method={"name": "show_template", "params": []}
            )[0]
