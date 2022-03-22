from ...bin.utils import Utils

from ..Screen import Screen


class CompetitionNameEdit(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "27", "CompetitionNameEdit")

    def text(self, text, user_id):

        event_id, competition_id = Utils.api("get",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id", "competition_id"], 
        )[0]

        team_id, events_ids = Utils.api("get_or_make",
        model="Competition",
        params={"id": competition_id},
        fields=["id", "events_ids"], 
        by=user_id
        )[0]

        Utils.api("update", 
        model="Competition",
        filter_params={"id": team_id},
        update_params={"name": text, "events_ids": f"{events_ids}{event_id};"}        
        )

        Utils.api("update", 
        model="Event",
        filter_params={"id": event_id},
        update_params={"competition_id": team_id}        
        )

        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]