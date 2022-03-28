import time

from attr import field

from ..Screen import Screen
from ...bin.utils import Utils

class Remainder(Screen):
    
    remainders = []

    @classmethod
    def _get_(cls, name=None, screen_id=None, remainder_id=None):
        
        for remainder in cls.remainders:
            if ((remainder.remainder_id == remainder_id or remainder_id is None) and (remainder.screen_id == screen_id or screen_id is None) and (remainder.remainder_name == name or name is None)): 
                return remainder

    def __init__(self, via, screen_id="-1", remainder_name="") -> None:
        
        super().__init__(via, screen_id, remainder_name)

        self.remainder_id = str(int(screen_id) - 100) if len(str(int(screen_id) - 100)) > 1 else f"0{str(int(screen_id) - 100)}"
        self.remainder_name = remainder_name

        self.remainders.append(self)

    def schedule(self, when, to_whom, formatters=None, group=None, callback_data=None):
        
        rv = []
        if type(when) is not list: when = [when,]
        
        for timestamp in when:
        
            rv.extend(Utils.api("execute_method",
            model="BotUser",
            params={"id": to_whom},
            method={"name": "send_remainder_to", "params": [self.screen_id, timestamp, formatters if formatters is not None else [[],], group, callback_data if callback_data is not None else [[],]]}
))

        return rv

    @classmethod
    def unschedule(self, group_name): # copilot: call Utils.api to update self.is_active to False (represented as int 0) and set self.pause_epoch to current_epoch (respresented as int of time.time())  
        
        scheduled_messages_ids = Utils.api("get",
        model="ScheduledMessage",
        params={"group_name": group_name},
        fields=["id",]
        )

        for scheduled_message_id in scheduled_messages_ids:
            Utils.api("update",
            model="ScheduledMessage",
            filter_params={"id": scheduled_message_id[0]},
            update_params={"is_active": 0, "pause_epoch": int(time.time())})
        
    @classmethod
    def reschedule(cls, group_name, add_time=True, new_time=None): # copilot: call Utils.api to update self.is_active to True (represented as int a), self.epoch to self.epoch + difference between int(time.time()) and self.pause_epoch, and set self.pause_epoch to an empty string ("")  

        scheduled_messages_ids = Utils.api("get",
        model="ScheduledMessage",
        params={"group_name": group_name},
        fields=["id",]
        )

        for scheduled_message_id in scheduled_messages_ids:
            epoch, pause_epoch = Utils.api("get",
            model="ScheduledMessage",
            params={"id": scheduled_message_id[0]},
            fields=["epoch", "pause_epoch"])[0]

            new_epoch = int(time.time()) + int(epoch) - int(pause_epoch) if add_time and new_time is None else epoch if new_time is None else new_time

            Utils.api("update",
            model="ScheduledMessage",
            filter_params={"id": scheduled_message_id[0]},
            update_params={"is_active": 1, "epoch": str(new_epoch) ,"pause_epoch": ""})

    @classmethod
    def assign_group(cls, scheduled_message_id, group_name):
        
        Utils.api("update",
        model="ScheduledMessage",
        filter_params={"id": scheduled_message_id},
        update_params={"group_name": group_name}
        )

    @classmethod
    def remove_group(cls, scheduled_message_id):
        
        Utils.api("update",
        model="ScheduledMessage",
        filter_params={"id": scheduled_message_id},
        update_params={"group_name": ""}
        )

    def button_0(self, params, user_id, scheduled_message_id):
        pass