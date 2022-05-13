from ....bin.utils import Utils
from ..Remainder import Remainder

class EventScheduled(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        ok = {"text": self.strings[1][0], "data": "r_0_04_{}"}
        start = {"text": self.strings[1][1], "data": "r_1_04_{}"}

        layout = [(ok, start),]
        
        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "104", "EventScheduled", bot_strings)

    def button_1(self, params, user_id, scheduled_message_id):      
        
        event_id, event_status, event_periods_ids, rules_set_id = Utils.api("get",
        model="Event",
        params={"id": int(params[0])},
        fields=["id", "status", "periods_ids", "rules_set_id"]
        )[0]

        coin_tosses_before_periods = Utils.api("get",
        model="RulesSet",
        params={"id": rules_set_id},
        fields=["coin_tosses_before_periods"]
        )[0][0]

        period_count = 0
        for period_id in event_periods_ids.split(";"):
            if period_id:
                period_count += 1

        if coin_tosses_before_periods[period_count] == 1: # not decreasing the period count as period is already inited
            
            return Utils.api("execute_method",
            model="Event",
            params={"id": int(params[0])},
            method={"name": "run", "params": ["coinToss_"]})[0]
        
        else: #TODO check?
            
            period_id = Utils.api("get_or_make",
            model="Period",
            params={"event_id": event_id, "status": 0},
            fields=["id"],)[0][0]

            return Utils.api("execute_method",
            model="Period",
            params={"id": period_id},
            method={"name": "start", "params": []}
            )[0]