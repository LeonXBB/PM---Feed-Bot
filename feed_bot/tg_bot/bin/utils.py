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
            except Exception as e: #TODO change to the specific type of an exception
                print(f"Exception {e} occured while making request to api, trying again...")
                #time.sleep(float(config("server_request_sleep_period"))) #TODO change to logger
                #done = True #TODO remove (see above)
                time.sleep(1)

        return rv

    @staticmethod
    def init_screens(via):
        
        from ..screens import all_screens

        for screen in all_screens:
            screen(via)