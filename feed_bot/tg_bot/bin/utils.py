from decouple import config

import time
import requests

class Utils:

    def get_token_for_post():
        pass # TODO: do

    @staticmethod
    def api(task, **kwargs):
        
        rv = None

        done = False
        while not done:
            try:
                rv = requests.post(f"{config('server_address')}/api", json={"task": task, **kwargs}).json()
                done = True
            except Exception as e: #TODO change to the specific type of an exception
                print(f"Exception {e} occured while making request to api, trying again...")
                time.sleep(float(config("request_sleep_period"))) #TODO change to logger
                done = True #TODO remove (see above)
        
        return rv

    @staticmethod
    def init_screens(via):
        
        from ..screens import all_screens

        for screen in all_screens:
            screen(via)