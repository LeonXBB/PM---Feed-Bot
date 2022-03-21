from ...bin.utils import Utils
from ..Screen import Screen


class HomeTeamNameEdit(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "22", "HomeTeamNameEdit")
    
    def text(self, text, user_id):

        event_id = Utils.api("get",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id"], 
        )[0][0]

        Utils.api("update", 
        model="Event",
        filter_params={"id": event_id},
        update_params={"delete_home_team_name": text}        
        )

        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]