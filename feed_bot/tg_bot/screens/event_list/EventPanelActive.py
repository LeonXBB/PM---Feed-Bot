from ...bin.utils import Utils
from ..Screen import Screen


class EventPanelActive(Screen):

    def get_keyboards(self, data=None, via=None):
            
            cancel = {"text": self.strings[1][0], "data": "d_43_0_{}"}
            control_panel = {"text": self.strings[1][1], "data": "d_43_1_{}"}

            layout = [(cancel, control_panel), ]
    
            return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "43", "EventPanelActive", bot_strings)

    def button_0(self, params, user_id):
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "cancel", "params": ["event",]}
        )[0]
        
    def button_1(self, params, user_id):
        
        event_id, event_status, event_periods_ids, rules_set_id = Utils.api("get",
        model="Event",
        params={"id": int(params[0])},
        fields=["id", "status", "periods_ids", "rules_set_id"]
        )[0]

        period_count = 0
        is_paused = 0

        for period_id in event_periods_ids.split(";"):
            if period_id:
                period_count += 1
                last_period_id = int(period_id)
                is_paused = Utils.api("get",
                model="Period",
                params={"id": last_period_id},
                fields=["is_paused",]
                )[0][0]

        coin_tosses_before_periods = Utils.api("get",
        model="RulesSet",
        params={"id": rules_set_id},
        fields=["coin_tosses_before_periods"]
        )[0][0]

        if event_status == 0: # being created
            
            return Utils.api("execute_method",
            model="Event",
            params={"id": event_id},
            method={"name": "show_template", "params": []}
            )[0]

        elif event_status == 1: # awaiting start

            if coin_tosses_before_periods[period_count] == 1: # not decreasing period count as period is already inited
                
                return Utils.api("execute_method",
                model="Event",
                params={"id": event_id},
                method={"name": "run", "params": ["coinToss_"]})[0]
            
            else:
                
                Utils.api("execute_method",
                model="Period",
                params={"id": last_period_id},
                method={"name": "launch", "params": []}
                )

                return Utils.api("execute_method",
                model="Period",
                params={"id": last_period_id},
                method={"name": "run", "params": ["show_"]}
                )[0]

        elif event_status == 3: #between periods

            if coin_tosses_before_periods[period_count] == 1: # not decreasing period count as period is already inited
                
                return Utils.api("execute_method",
                model="Event",
                params={"id": event_id},
                method={"name": "run", "params": ["coinToss_"]})[0]
            
            else:
                
                Utils.api("execute_method",
                model="Period",
                params={"id": last_period_id},
                method={"name": "launch", "params": []}
                )

                return Utils.api("execute_method",
                model="Period",
                params={"id": last_period_id},
                method={"name": "run", "params": ["show_"]}
                )[0]

        elif event_status == 2: #in progress
            
            if is_paused:

                return Utils.api("execute_method",
                model="Event",
                params={"id": event_id},
                method={"name": "show_paused_match_template", "params": [last_period_id, ]}
                )[0]
            
            else:
                
                return Utils.api("execute_method",
                model="Event",
                params={"id": event_id},
                method={"name": "show_match_template", "params": [last_period_id, ]}
                )[0]

        elif event_status == 4: #finished
            
            return Utils.api("execute_method",
            model="Event",
            params={"id": event_id},
            method={"name": "show_paused_match_template", "params": [last_period_id, ]}
            )[0]