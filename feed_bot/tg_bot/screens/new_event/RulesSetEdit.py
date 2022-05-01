from ...bin.utils import Utils

from ..Screen import Screen

class RulesSetEdit(Screen):

    def get_keyboards(self, data=None, via=None): # TODO do not forget to (dynamically) update the keyboard list when we allow users to make their own rules sets
        
        layout = []

        if via == "bot":
           
            all_rules_sets = Utils.api("get_all",
            model="RulesSet",
            fields=["id", "name"]
            )

        elif via == "server":

            from ...models import RulesSet

            rules_sets = RulesSet.objects.all().order_by("id")
            all_rules_sets = []
            for rules_set in rules_sets:
                all_rules_sets.append([rules_set.id, rules_set.name])

        for rules_set in all_rules_sets:
            layout.append(({"text": [rules_set[1], rules_set[1], rules_set[1], rules_set[1], rules_set[1]], "data": f"0_{rules_set[0]}"},))

        return_button = {"text": self.strings[1][0], "data": "1_0"}
        layout.append((return_button,))

        return [layout, ]

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "26", "RulesSetEdit", bot_strings)

    def button_0(self, params, user_id):

        event_id = Utils.api("get",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id",], 
        )[0][0]

        Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "update_template", "params": ["rules_set_id", int(params[0])]},
        )

        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]

    def button_1(self, params, user_id):
        
        event_id = Utils.api("get",
        model="Event",
        params={"admin_id": user_id, "status": 0},
        fields=["id"], 
        )[0][0] 
        
        return Utils.api("execute_method",
        model="Event",
        params={"id": event_id},
        method={"name": "show_template", "params": []}
        )[0]