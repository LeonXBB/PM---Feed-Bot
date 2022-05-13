from decouple import config

from ..Screen import Screen
from ...bin.utils import Utils

class LanguageSelection(Screen):

    def __init__(self, via, bot_strings=None) -> None:
        super().__init__(via, "11", "LanguageSelection", bot_strings)

    def get_keyboards(self, data=None, via=None):
        
        layout = []

        if via == "bot":

            rv = Utils.api("get_all",
            model="TextLanguage"
            )

        elif via == "server":
    
            from ...models import TextLanguage
                
            languages = TextLanguage.objects.all().order_by("id")
            rv = []
            for language in languages:
                rv.append([language.id, language.self_name])

        for language in rv:
            layout.append(list())
            layout[-1].append({"text": [language[1], language[1], language[1], language[1], language[1]], "data": f"0_{language[0]}"})

        return [layout, ]

    def button_0(self, params, user_id):
        Utils.api("update",
        model="BotUser",
        filter_params={"id": user_id},
        update_params={"language_id": params[0]}
        )
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")], ]]} #TODO move static formatters into screen class?
        )[0]
