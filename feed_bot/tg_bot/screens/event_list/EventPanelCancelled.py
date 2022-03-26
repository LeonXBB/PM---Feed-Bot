from ..Screen import Screen


class EventPanelCancelled(Screen):

    def get_keyboards(self):

        restore = {"text": self.strings[1][0], "data": "0_0"}

        layout = [(restore,), ]

        return [layout,]

    def __init__(self, via) -> None:
        super().__init__(via, "44", "EventPanelCancelled")

    def button_0(self, params, user_id):

        print(0)