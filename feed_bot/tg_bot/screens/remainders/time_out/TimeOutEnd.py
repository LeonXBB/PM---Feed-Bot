from ....bin.utils import Utils
from ..Remainder import Remainder


class TimeOutEnd(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        ok = {"text": self.strings[1][0], "data": "r_0_21_{}"}
        
        layout = [(ok,),]
        
        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "121", "TimeOutEnd", bot_strings)

    def button_0(self, params, user_id, scheduled_message_id): #TODO move to Period.run

        event_id = int(params[3])

        period_id, left_team_id, right_team_id = Utils.api("get",
        model="Period",
        params={"event_id": event_id},
        fields=["id", "left_team_id", "right_team_id"]
        )[-1]

        time_out_id, team_id = Utils.api("get",
        model="TimeOut",
        params={"event_id": event_id, "period_id": period_id, "team_id": left_team_id if params[5] == 0 else right_team_id, "at_score": f"{params[-1]}"}, 
        fields=["id", "team_id"]
        )[0]

        Utils.api("time_out_ended", "logic", period_count=params[1], time_out_id=time_out_id, event_id=event_id, team_id=team_id, period_id=period_id)

        return Utils.api("execute_method",
        model="Period",
        params={"id": period_id},
        method={"name": "run", "params": ["pauseResume_"]}
        )[0]