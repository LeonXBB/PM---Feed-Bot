from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..Screen import Screen


class ControlPanelPaused(Screen):

    def get_keyboards(self):
        
        super().get_keyboards()

        resume = InlineKeyboardButton(["Resume event", ], callback_data="0_0")
     
        cancel = InlineKeyboardButton(["Cancel",], callback_data="3_0")
        main_menu = InlineKeyboardButton(["Main Menu",], callback_data="4_0")
        
        layout = [(resume, ), (cancel, main_menu)]

        keyboard = InlineKeyboardMarkup(layout)

        return [keyboard, ]

    def __init__(self, via) -> None:
        super().__init__(via, "31", "ControlPanelPaused")

        # '''PAUSED\n\nTeam 1 - Team 2\n\n3 - 1\n(1-0)\n\nTime-outs:\n1 / 0''', ]}#self.strings[0]

        #self.strings = self.strings[0]
            
    def button_0(self, params, user_id): # resume
        pass

    def button_1(self, params, user_id): # cancel
        pass

    def button_2(self, params, user_id): # main_menu
        pass
