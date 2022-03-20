from decouple import config

import hashlib

from ..Screen import Screen
from ...bin.utils import Utils

class AuthorizationWrongPassword(Screen):

    def __init__(self, via) -> None:
        super().__init__(via, "01", "AuthorizationWrongPassword")

    def text(self, text, user_id):

        found_pass_obj = Utils.api("get",
        model="PasswordPair",
        fields=["id", "user_id"],
        params={"password_sha256": hashlib.sha256(text.encode()).hexdigest()}
        )

        user_pass_id = Utils.api("get",
        model="BotUser",
        fields=["password_id",],
        params={"id": user_id}
        )[0][0]
        
        if len(found_pass_obj) > 0 and len(found_pass_obj[0]) > 0:
            found_pass_id = found_pass_obj[0][0]
            found_pass_user_id = found_pass_obj[0][1]

            if (found_pass_user_id == -1 and user_pass_id == -1) or (found_pass_user_id == user_id and found_pass_id == user_pass_id):

                if found_pass_user_id == -1 and user_pass_id == -1:
                    
                    Utils.api("execute_method", 
                    model="PasswordPair",
                    params={"password_sha256": hashlib.sha256(text.encode()).hexdigest()},
                    method={"name": "assign_to_user", "params": [user_id, ]}
                    )

                Utils.api("update", 
                model="BotUser",
                filter_params={"id": user_id},
                update_params={"is_logged_in": 1}
                )
                
                return Utils.api("execute_method", 
                model="BotUser",
                params={"id": user_id},
                method={"name": "show_screen_to", "params": ["10", [[config("telebot_version")], ]]} #TODO move static formatters into screen class?
                )[0]
            
        return Utils.api("execute_method", 
        model="BotUser",
        params={"id": user_id},
        method={"name": "show_screen_to", "params": ["01",]}
        )[0]