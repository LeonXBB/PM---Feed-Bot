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
                rv = requests.post(f"{config('output_protocol')}://{config('output_address')}/api{subdomain}", json={"task": task, **kwargs}).json()
                done = True
            except Exception as e:
                time.sleep(1) #TODO : make it configurable

        return rv

    @staticmethod
    def init_screens(via):
        
        from ..screens import all_screens

        if via == "server":
            with open("screen_strings.txt", "w+", encoding="utf-8") as file:
                file.write("{")

        elif via == "bot" or via == "scheduling":
            with open("feed_bot/screen_strings.txt", "r", encoding="utf-8") as file:
                raw_strings = file.read()
                screen_strings = eval(raw_strings)

        for screen in all_screens:
            try:
                print(time.strftime("%H:%M:%S"), f"Initializing screen {screen.__name__} for {via}")
                screen(via) if via == "server" else screen("bot", screen_strings[screen.__name__])
                print(time.strftime("%H:%M:%S"), f"Screen {screen.__name__} initialized for {via}")
            except Exception as e:
                print(e)

        if via == "server":
            with open("screen_strings.txt", "a", encoding="utf-8") as file:
                file.write("}")