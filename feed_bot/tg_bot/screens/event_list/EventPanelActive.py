from ..Screen import Screen


class EventPanelActive(Screen):

    def get_keyboards(self):
            
            cancel = {"text": self.strings[1][0], "data": "0_0"}
            control_panel = {"text": self.strings[1][1], "data": "1_0"}

            layout = [(cancel, control_panel), ]
    
            return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "43", "EventPanelActive")

    def button_0(self, params, user_id):
        
        print(0)

    def button_1(self, params, user_id):
        
        print(1)