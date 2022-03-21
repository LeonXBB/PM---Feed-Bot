from ...bin.utils import Utils
from ..Screen import Screen


class AwayTeamNameEdit(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "23", "AwayTeamNameEdit")

    def text(self, text, user_id):

        event_id = Utils.api("get",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id"], 
        )[0]

        if type(event_id) is list: event_id = event_id[0] #TODO fix

        Utils.api("update", 
        model="Event",
        filter_params={"id": event_id},
        update_params={"delete_away_team_name": text}        
        )

        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]