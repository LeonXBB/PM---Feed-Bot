import re
from decouple import config

from ...bin.utils import Utils
from ..Screen import Screen


class ControlPanelActive(Screen):

    def get_keyboards(self, data=None):
        
        if data is None:
            return super().get_keyboards()

        ball_string = Utils.api("get",
        model="TextString",
        params={"screen_id": "active", "position_index": 0},
        fields=["language_1", "language_2", "language_3", "language_4", "language_5"]
        )[0]

        time_out_string = Utils.api("get",
        model="TextString",
        params={"screen_id": "active", "position_index": 1},
        fields=["language_1", "language_2", "language_3", "language_4", "language_5"]
        )[0]

        period_id = data[4][0][0]
        left_team_id, right_team_id, ball_possesion_team_id, event_id, timeouts_ids = Utils.api("get",
        model="Period",
        params={"id": int(period_id)},
        fields=["left_team_id", "right_team_id", "ball_possesion_team_id", "event_id", "timeouts_ids"]
        )[0]

        rules_set_id, periods_ids = Utils.api("get",
        model="Event",
        params={"id": event_id},
        fields=["rules_set_id", "periods_ids"]
        )[0]

        period_count = 0
        for period_id in periods_ids.split(";"):
            if period_id:
                period_count += 1
            
        scores_names, time_outs_per_team_per_period, actions_list = Utils.api("get",
        model="RulesSet",
        params={"id": int(rules_set_id)},
        fields=["scores_names", "time_outs_per_team_per_period", "actions_list"]
        )[0]

        team_in_possesion = "left" if ball_possesion_team_id == left_team_id else "right" if ball_possesion_team_id == right_team_id else "neutral"

        left_button = {"text": ball_string if team_in_possesion != "left" else self.strings[1][2], "data": f"2_0_{0 if team_in_possesion != 'left' else 1}" + "_{}"}
        middle_button = {"text": ball_string if team_in_possesion != "neutral" else self.strings[1][2], "data": f"2_1_{0 if team_in_possesion != 'neutral' else 1}" + "_{}"}
        right_button = {"text": ball_string if team_in_possesion != "right" else self.strings[1][2], "data": f"2_2_{0 if team_in_possesion != 'right' else 1}" + "_{}"}

        header = (left_button, middle_button, right_button)
        points = []
        time_outs = []
        actions = []

        for i, score_name in enumerate(scores_names.split(";")):
            if score_name:
                points.append(list())
                for team in range(2):
                    points[-1].append({"text": [score_name, score_name, score_name, score_name, score_name], "data": f"3_{team}_{i}" + "_{}"})

        if max(list( int(time_out_per_team) for time_out_per_team in (time_outs_per_team_per_period.split(";")[period_count - 1].split(",")) )) > 0:
            
            time_outs_count = [0, 0]
            for time_out_id in timeouts_ids.split(";"):
                
                if time_out_id:
                    team_id, is_technical = Utils.api("get",
                    model="TimeOut",
                    params={"id": int(time_out_id)},
                    fields=["team_id", "is_technical"]
                    )[0]

                    if is_technical == 0: time_outs_count[team_id != left_team_id] += 1
        
            for team in range(2):
                if time_outs_count[team] < int(time_outs_per_team_per_period.split(";")[period_count - 1].split(",")[team]):
                    time_outs.append({"text": self.strings[1][4], "data": f"4_{team}_1" + "_{}"})
                else:
                    time_outs.append({"text": self.strings[1][3], "data": f"4_{team}_0" + "_{}"})

        for i, action in enumerate(actions_list.split(";")):
            actions.append(list())
            for team in range(2):
                actions[-1].append({"text": [action, action, action, action, action], "data": f"5_{team}_{i}" + "_{}"})

        cancel = {"text": self.strings[1][0], "data": "0_{}"}
        go_back = {"text": self.strings[1][1], "data": "1_{}"}

        controls = (cancel, go_back)

        layout = [header, *points, time_outs, *actions, controls]

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "30", "ControlPanelActive")
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
        
        team, score_type, period_id = params

        return Utils.api("execute_method",
        model="Period",
        params={"id": int(period_id)},
        method={"name": "run", "params": [f"point_{team}_{score_type}", ]}
        )[0]

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
