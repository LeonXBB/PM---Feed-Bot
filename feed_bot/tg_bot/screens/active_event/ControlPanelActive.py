from decouple import config

import time

from ...bin.utils import Utils
from ..Screen import Screen

from .._utils.checks import check_time_outs

class ControlPanelActive(Screen):

    def get_keyboards(self, data=None, via=None): # TODO rewrite in respect to via server / bot
        
        def get_ball_string() -> list:
            return Utils.api("get",
            model="TextString",
            params={"screen_id": "active", "position_index": 0},
            fields=["language_1", "language_2", "language_3", "language_4", "language_5"]
            )[0]
    
        def get_period_data() -> list:
            return [data[4][0][0], *Utils.api("get",
            model="Period",
            params={"id": int(data[4][0][0])},
            fields=["left_team_id", "right_team_id", "ball_possesion_team_id", "event_id"]
            )[0]]

        def get_event_data() -> list:
            return Utils.api("get",
            model="Event",
            params={"id": event_id},
            fields=["rules_set_id",]
            )[0][0]

        def get_period_count() -> list:
            return len(Utils.api("get",
            model="Period",
            params={"event_id": event_id},
            fields=["id",])) #TODO check for 0th index 

        def get_rules():
            return Utils.api("get",
            model="RulesSet",
            params={"id": rules_set_id},
            fields=["scores_names", "actions_list"]
            )[0]

        def get_head_row_button(index):
            
            team_in_possesion = 0 if ball_possesion_team_id == left_team_id else 2 if ball_possesion_team_id == right_team_id else 1

            return {"text": ball_string if team_in_possesion != index else self.strings[1][2], "data": f"2_{index}_{0 if team_in_possesion != index else 1}" + "_{}"}

        def get_point_buttons():
            
            def get_point_button(team_side_index, score_type_index, score_name):
                return {"text": [score_name, score_name, score_name, score_name, score_name], "data": f"3_{team_side_index}_{score_type_index}" + "_{}"}
            
            rv = []

            for i, score_name in enumerate(scores_names):
                rv.append(list())
                for team_side_index in range(2):
                    rv[-1].append(get_point_button(team_side_index, i, score_name))

            return rv
        
        def get_time_out_buttons():

            rv = []

            def get_time_out_count(team_side_index):
                
                from ...models import TimeOut

                return len(TimeOut._get_({"event_id": event_id, "period_id": period_id, "team_id": [left_team_id, right_team_id][team_side_index], "is_technical": 0}))

                #return len(Utils.api("get",
                #model="TimeOut",
                #params={"event_id": event_id, "period_id": period_id, "team_id": [left_team_id, right_team_id][team_side_index], "is_technical": 0},
                #fields=["id",]
                #))

            def get_time_out_button(team_side_index, active):
                return {"text": self.strings[1][active + 3], "data": f"4_{team_side_index}_{active}" + "_{}"}
                                     
            for team_side_index in range(2):
                res = check_time_outs(team_side_index, event_id) # 0 - no time outs in period, 1 - time outs in period, 2 - time outs in period and available
                if res != 0:    
                    rv.append(get_time_out_button(team_side_index, res-1))

            return rv

        def get_action_buttons():

            def get_action_button(team_side_index, action_index, action_name):
                return {"text": [action_name, action_name, action_name, action_name, action_name], "data": f"5_{team_side_index}_{action_index}" + "_{}"}

            rv = []

            for action_index, action_name in enumerate(actions_list):
                rv.append(list())
                for team_side_index in range(2):
                    rv[-1].append(get_action_button(team_side_index, action_index, action_name))

            return rv

        if data is None:
            return super().get_keyboards()

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 0 / 10")

        ball_string = get_ball_string()
 
        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 1 / 10")

        period_id, left_team_id, right_team_id, ball_possesion_team_id, event_id = get_period_data()

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 2 / 10")

        rules_set_id = get_event_data()

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 3 / 10")

        period_count = get_period_count()

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 4 / 10")

        scores_names, actions_list = get_rules()

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 5 / 10")

        header = [get_head_row_button(i) for i in range(3)]

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 6 / 10")

        if (res:= get_point_buttons()) is not None: points = [*res]

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 7 / 10")

        time_outs = get_time_out_buttons()

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 8 / 10")

        if (res:= get_action_buttons()) is not None: actions = [*res]

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 9 / 10")

        cancel = {"text": self.strings[1][0], "data": "0_{}"}
        go_back = {"text": self.strings[1][1], "data": "1_{}"}

        controls = (cancel, go_back)

        layout = [row for row in [header, *points, time_outs, *actions, controls] if row is not None and len(row) > 0]

        print(time.strftime("%H:%M:%S"), "Getting keyboards for active event screen, 10 / 10")

        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "30", "ControlPanelActive", bot_strings)
        delattr(self, "keyboards")
           
    def button_0(self, params, user_id): # cancel
        pass

    def button_1(self, params, user_id): # go back

        return Utils.api("execute_method",
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")]]]} #TODO static formatters into separate file
        )[0]

    def button_2(self, params, user_id): # header
        
        if params[1] == "1": # pause
            
            event_id = int(params[2])

            return Utils.api("execute_method",
            model="Period",
            params={"id": event_id},
            method={"name": "run", "params": ["pauseResume_"]}
            )[0]

        elif params[1] == "0": # ball_control
            
            button_number = int(params[0]) # 0 - left, 1 - neutral, 2 - right

            event_id = int(params[2])

            return Utils.api("execute_method",
            model="Period",
            params={"id": event_id},
            method={"name": "run", "params": [f"ballControl_{button_number}",]}
            )[0]

    def button_3(self, params, user_id): # point type
        
        from ...models import Period

        print(time.strftime("%H:%M:%S"), "New point. Getting params...")

        team, score_type, period_id = params

        print(time.strftime("%H:%M:%S"), "Got params. Calling manager function...")

        return Period._get_({"id": int(period_id)})[0].run(f"point_{team}_{score_type}")
        
        #return Utils.api("execute_method",
        #model="Period",
        #params={"id": int(period_id)},
        #method={"name": "run", "params": [f"point_{team}_{score_type}", ]}
        #)[0]

    def button_4(self, params, user_id): # time out
        
        team, active, period_id = params

        if active == "1":

            return Utils.api("execute_method",
            model="Period",
            params={"id": int(period_id)},
            method={"name": "run", "params": [f"timeOut_{team}", ]}
            )[0]

    def button_5(self, params, user_id): # action
        
        team, action_type, period_id = params

        return Utils.api("execute_method",
        model="Period",
        params={"id": int(period_id)},
        method={"name": "run", "params": [f"action_{team}_{action_type}", ]}
        )[0]
