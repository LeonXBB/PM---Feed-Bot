from ....bin.utils import Utils
from ..Remainder import Remainder


class TimeOutStart(Remainder):

    def get_keyboards(self):
        
        start = {"text": self.strings[1][0], "data": "r_0_20_0"}
        skip = {"text": self.strings[1][1], "data": "r_1_20_{}"}
        
        layout = [(start, skip),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "120", "TimeOutStart")

    def button_1(self, params, user_id, scheduled_message_id): # skip  
        
        Remainder.unschedule("_".join(params))

        event_id = int(params[3])

        periods_ids = Utils.api("get",
        model="Event",
        params={"id": event_id},
        fields=["periods_ids"]
        )[0][0]

        for period_id_ in periods_ids.split(";"):
            if period_id_: period_id = int(period_id_) 

        return Utils.api("execute_method",
        model="Period",
        params={"id": period_id},
        method={"name": "run", "params": ["pauseResume_"]}
        )[0]