from ....bin.utils import Utils
from ..Remainder import Remainder


class TechnicalTimeOutEnd(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        ok = {"text": self.strings[1][0], "data": "r_0_31_{}"}
        
        layout = [(ok,),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "131", "TechnicalTimeOutEnd")

    def button_0(self, params, user_id, scheduled_message_id): #TODO move to Period.run
        
        event_id = int(params[3])

        period_id = Utils.api("get",
        model="Period",
        params={"event_id": event_id},
        fields=["id",]
        )[-1][0]

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