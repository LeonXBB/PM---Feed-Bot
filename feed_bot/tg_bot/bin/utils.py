from decouple import config

import time
import requests

class Utils:

    def get_token_for_post():
        pass # TODO: do

    @staticmethod
    def api(task, subdomain="", **kwargs):
        
        rv = None

        if len(subdomain) > 0: subdomain = f"/{subdomain}"

        done = False
        while not done:
            try:
                rv = requests.post(f"{config('url_server_address')}/api{subdomain}", json={"task": task, **kwargs}).json()
                done = True
            except Exception as e:
                with open("api_errors_log.txt", "w+", encoding="utf-8") as f:
                    f.write(f"{time.time()}: {e}")
                time.sleep(1)

        return rv

    @staticmethod
    def init_screens(via):
        
        from ..screens import all_screens

        for screen in all_screens:
            try:
                screen(via)
            except Exception as e:
                print(e)
