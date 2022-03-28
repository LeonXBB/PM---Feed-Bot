from ...bin.utils import Utils
from ..Screen import Screen


class ControlPanelPaused(Screen):

    #def get_strings(self):
    #    return super().get_strings(via)

    def get_keyboards(self):
        
        resume = {"text": self.strings[1][0], "data": "0_{}}"}
     
        cancel = {"text": self.strings[1][0], "data": "1_{}"}
        main_menu = {"text": self.strings[1][0], "data": "2_{}"}
        
        layout = [(resume, ), (cancel, main_menu)]

        return [layout, ]

    def __init__(self, via) -> None:

        super().__init__(via, "31", "ControlPanelPaused")
        #delattr(self, "strings")
            
    def button_0(self, params, user_id): # resume
        pass

    def button_1(self, params, user_id): # cancel
        pass

    def button_2(self, params, user_id): # main_menu
        pass
