from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..Screen import Screen


class ControlPanelActive(Screen):

    def get_keyboards(self):
        
        #pause = InlineKeyboardButton(["Pause event", ], data="0_0")
        #ball_control_change = InlineKeyboardButton(["⚽", ], callback_data="5_0") #TODO 3 positions
        
        #TODO remember, multiple points
        #point_home_team = InlineKeyboardButton(["Point team Team 1"], callback_data="1_0")
        #point_away_team = InlineKeyboardButton(["Point team Team 2",], callback_data="1_1")
        
        #time_out_home_team = InlineKeyboardButton(["Time out Team 1",], callback_data="2_0") #TODO if none
        #time_out_away_team = InlineKeyboardButton(["Time out Team 2",], callback_data="2_1")

        #cancel = InlineKeyboardButton(["Cancel",], callback_data="3_0")
        #main_menu = InlineKeyboardButton(["Main Menu",], callback_data="4_0")

        #layout = [(pause, ball_control_change), (point_home_team, point_away_team), (time_out_home_team, time_out_away_team), (cancel, main_menu)]
        
    
        #keyboard = InlineKeyboardMarkup(layout)

        #return [keyboard, ]
        return [None, ]
    def __init__(self, via) -> None:
        super().__init__(via, "30", "ControlPanelActive")
           
    def button_0(self, params, user_id): # new event
        print("new event")

    def button_1(self, params, user_id): # event list
        print("event_list")

    def button_2(self, params, user_id): # set rules editor
        print("set rules editor")

    def button_3(self, params, user_id): # language_selection
        print("language selection")

    def button_4(self, params, user_id): # exit
        print("exit")