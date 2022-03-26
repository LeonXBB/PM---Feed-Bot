from ....bin.utils import Utils
from ..Remainder import Remainder

import time

class EventScheduled(Remainder):

    def get_keyboards(self):
        
        ok = {"text": self.strings[1][0], "data": "r_0_04_test"}
        start = {"text": self.strings[1][1], "data": "r_1_04_test"}

        layout = [(ok, start),]
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "104", "EventScheduled")

    def button_1(self, params, user_id, message_id, scheduled_message_id):      
        
        group_name = Utils.api("get", model="ScheduledMessage", params={"id": scheduled_message_id}, fields=["group_name"])[0][0]
        
        Remainder.unschedule(group_name)
        time.sleep(10)
        Remainder.reschedule(group_name)