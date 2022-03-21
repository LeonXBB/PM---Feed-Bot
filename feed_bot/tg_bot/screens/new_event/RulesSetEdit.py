from ...bin.utils import Utils

from ..Screen import Screen

class RulesSetEdit(Screen):

    def get_keyboards(self): # TODO WRITE
        
        classic_volleyball = {"text": self.strings[1][1], "data": "0_0"}
        return_ = {"text": self.strings[1][0], "data": "0_0"}

        layout = [(return_,), (classic_volleyball,)]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "26", "RulesSetEdit")

    def button_0(self, params, user_id):

        event_id = Utils.api("get_or_make",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id"], 
        )[0]

        if type(event_id) is list: event_id = event_id[0] #TODO fix

        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]