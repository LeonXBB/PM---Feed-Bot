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

        self.remainder_id = str(int(screen_id) - 100)
        self.remainder_name = remainder_name

        self.remainders.append(self)

    def schedule(self, when, to_whom, formatters=None):
        
        rv = []
        if type(when) is not list: when = [when,]
        
        for timestamp in when:
        
            rv.extend(Utils.api("execute_method",
            model="BotUser",
            params={"id": to_whom},
            method={"name": "send_remainder_to", "params": [self.screen_id, timestamp, formatters if formatters is not None else [[],]]}
            ))

        return rv

    def unschedule(self):
        pass

    def reschedule(self):
        pass

    def assign_group(self):
        pass
    
    def clear_group(self):
        pass

    def button_0(self, params, user_id, message_id): # TODO find a way to move this stuff t
        