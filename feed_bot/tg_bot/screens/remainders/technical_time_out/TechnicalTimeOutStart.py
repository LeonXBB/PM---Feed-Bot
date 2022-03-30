from ....bin.utils import Utils
from ..Remainder import Remainder


class TechnicalTimeOutStart(Remainder):

    def get_keyboards(self):
        
        start = {"text": self.strings[1][0], "data": "r_0_30_0"}
        skip = {"text": self.strings[1][1], "data": "r_1_30_{}"}
        
        layout = [(start, skip),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "130", "TechnicalTimeOutStart")

    def button_1(self, params, user_id, scheduled_message_id): # skip  
        
        #TODO figure out why two arguments don't work here and in regular time out

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