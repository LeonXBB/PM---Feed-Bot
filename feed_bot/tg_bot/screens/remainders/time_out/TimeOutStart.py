from ....bin.utils import Utils
from ..Remainder import Remainder


class TimeOutStart(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        start = {"text": self.strings[1][0], "data": "r_0_20_0"}
        skip = {"text": self.strings[1][1], "data": "r_1_20_{}"}
        
        layout = [(start, skip),]
        
        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "120", "TimeOutStart", bot_strings)

    def button_1(self, params, user_id, scheduled_message_id): # skip  #TODO move to Period.run
        
        Remainder.unschedule("_".join(params))

        event_id = int(params[3])

        periods_ids = Utils.api("get",
        model="Event",
        params={"id": event_id},
        fields=["periods_ids"]
        )[0][0]

        for period_id_ in periods_ids.split(";"):
            if period_id_: period_id = int(period_id_) 

        left_team_id, right_team_id = Utils.api("get",
        model="Period",
        params={"event_id": event_id},
        fields=["left_team_id", "right_team_id"]
        )[-1]

        time_out_id, team_id = Utils.api("get",
        model="TimeOut",
        params={"event_id": event_id, "period_id": period_id, "team_id": left_team_id if params[5] == "0" else right_team_id, "at_score": f"{params[-1]}"}, 
        fields=["id", "team_id"]
        )[0]

        Utils.api("time_out_ended", "logic", period_count=params[1], time_out_id=time_out_id, event_id=event_id, team_id=team_id, period_id=period_id)

        return Utils.api("execute_method",
        model="Period",
        params={"id": period_id},
        method={"name": "run", "params": ["pauseResume_"]}
        )[0]