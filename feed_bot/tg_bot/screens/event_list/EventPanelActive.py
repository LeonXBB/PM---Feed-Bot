from ...bin.utils import Utils
from ..Screen import Screen


class EventPanelActive(Screen):

    def get_keyboards(self):
            
            cancel = {"text": self.strings[1][0], "data": "d_43_0_{}"}
            control_panel = {"text": self.strings[1][1], "data": "d_43_1_{}"}

            layout = [(cancel, control_panel), ]
    
            return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "43", "EventPanelActive")

    def button_0(self, params, user_id):
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "cancel", "params": ["event",]}
        )[0]
        
    def button_1(self, params, user_id):
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "show_match_template", "params": []}
        )[0]