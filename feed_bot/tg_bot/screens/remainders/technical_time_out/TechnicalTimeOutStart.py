from ....bin.utils import Utils
from ..Remainder import Remainder


class TechnicalTimeOutStart(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        start = {"text": self.strings[1][0], "data": "r_0_30_0"}
        skip = {"text": self.strings[1][1], "data": "r_1_30_{}"}
        
        layout = [(start, skip),]
        
        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "130", "TechnicalTimeOutStart", bot_strings)

    def button_1(self, params, user_id, scheduled_message_id): # skip #TODO move to Period.run 
        
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

        time_out_id = Utils.api("get",
        model="TimeOut",
        params={"event_id": event_id, "period_id": period_id, "is_technical": 1, "at_score": f"{params[-1]}"}, 
        fields=["id",]
        )[0][0]

        Utils.api("technical_time_out_ended", "logic", period_count=params[1], time_out_id=time_out_id, event_id=event_id, period_id=period_id)

        return Utils.api("execute_method",
        model="Period",
        params={"id": period_id},
        method={"name": "run", "params": ["pauseResume_"]}
        )[0]