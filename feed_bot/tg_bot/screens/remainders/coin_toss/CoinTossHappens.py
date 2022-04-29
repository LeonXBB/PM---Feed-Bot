import time

from ....bin.utils import Utils
from ..Remainder import Remainder


class CoinTossHappens(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        enter = {"text": self.strings[1][0], "data": "r_1_40_{}"}

        layout = ((enter,),)
        
        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "140", "CoinTossHappens")

    def button_1(self, params, user_id, scheduled_message_id):

        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "run", "params": ["coinToss_"]})[0]