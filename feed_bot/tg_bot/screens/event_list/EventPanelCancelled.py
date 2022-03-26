from ...bin.utils import Utils
from ..Screen import Screen


class EventPanelCancelled(Screen):

    def get_keyboards(self):

        restore = {"text": self.strings[1][0], "data": "d_44_0_{}"}

        layout = [(restore,), ]

        return [layout,]

    def __init__(self, via) -> None:
        super().__init__(via, "44", "EventPanelCancelled")

    def button_0(self, params, user_id):
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "cancel", "params": ["cancel_event",]}
        )[0]