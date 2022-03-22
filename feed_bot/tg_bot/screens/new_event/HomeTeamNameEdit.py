from ...bin.utils import Utils
from ..Screen import Screen


class HomeTeamNameEdit(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "22", "HomeTeamNameEdit")
    
    def text(self, text, user_id):

        event_id, home_team_id = Utils.api("get",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id", "home_team_id"], 
        )[0]

        team_id, events_ids = Utils.api("get_or_make",
        model="Team",
        params={"id": home_team_id},
        fields=["id", "events_ids"], 
        by=user_id
        )[0]

        Utils.api("update", 
        model="Team",
        filter_params={"id": team_id},
        update_params={"name": text, "events_ids": f"{events_ids}{event_id};"}        
        )

        Utils.api("update", 
        model="Event",
        filter_params={"id": event_id},
        update_params={"home_team_id": team_id}        
        )

        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]