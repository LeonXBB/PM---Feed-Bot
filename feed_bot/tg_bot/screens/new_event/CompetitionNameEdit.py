from ...bin.utils import Utils
from ..Screen import Screen


class CompetitionNameEdit(Screen):

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "27", "CompetitionNameEdit", bot_strings)

    def text(self, text, user_id):

        event_id, competition_id = Utils.api("get",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id", "competition_id"], 
        )[0]

        competition_id, events_ids = Utils.api("get_or_make",
        model="Competition",
        params={"id": competition_id, "name": text},
        fields=["id", "events_ids"], 
        by=user_id
        )[0]

        Utils.api("update", 
        model="Competition",
        filter_params={"id": competition_id},
        update_params={"name": text, "events_ids": f"{events_ids}{event_id};"}        
        )

        Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "update_template", "params": ["competition_id", competition_id]},
        )
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]