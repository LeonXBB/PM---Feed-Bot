from ....bin.utils import Utils
from ..Remainder import Remainder


class CoinTossAboutToHappen(Remainder):

    def get_keyboards(self, data=None, via=None):
        
        ok = {"text": self.strings[1][0], "data": "r_0_41_{}"}
        now = {"text": self.strings[1][1], "data": "r_1_41_{}"}

        layout = ((ok, now),)

        return [layout, ]

    def __init__(self, via) -> None:
        super().__init__(via, "141", "CoinTossAboutToHappen")

    def button_1(self, params, user_id, scheduled_message_id):

        return Utils.api("execute_method",
        model="Event",
        params={"id": int(params[0])},
        method={"name": "run", "params": ["coinToss_"]})[0]