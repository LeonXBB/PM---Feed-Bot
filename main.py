import multiprocess as mp

from decouple import config

import subprocess
import os
import time

from feed_bot.tg_bot.bin.main import FeedBot

if __name__ == "__main__":

    def start_server():
          
        os.chdir('feed_bot')
        #subprocess.run("daphne -v 0 meta.asgi:application")
        try:
            #for app_name in ("tg_bot", "website"):
            #    subprocess.run(f"python manage.py makemigrations {app_name}")
            #    subprocess.run(f"python manage.py migrate --database default")
            subprocess.run(f"python manage.py runserver {config('input_address', default='0.0.0.0')}:{config('PORT', default='80')}")
        except:
            #for app_name in ("tg_bot", "website"):
            #    subprocess.run(["python", "manage.py", "makemigrations", f"{app_name}"])
            #    subprocess.run(["python", "manage.py", "migrate", "--database", "default"])
            subprocess.run(["python", "manage.py", "runserver", f"{config('input_address', default='0.0.0.0')}:{config('PORT', default='80')}"])
        os.chdir("..")

    def start_bot():
        
        global bot 
        bot = FeedBot()
        bot.run()

    def start_scheduling():
        
        print("initin scheduling...")
        scheduling = mp.Process(target=bot.connection.run_schedule, name="scheduling", args=(bot, ))
        print("scheduling created")
        scheduling.start()
        print("scheduling started")

    def main():

        try:
            mp.set_start_method('spawn')
        except Exception as e:
            print(e)

        server_process = mp.Process(target=start_server, name="server")
        bot_process = mp.Process(target=start_bot, name="bot")
        scheduling_process = mp.Process(target=start_scheduling, name="scheduling")

        server_process.start()
        bot_process.start()
        scheduling_process.start()

        server_process.join()
        bot_process.join()
        scheduling_process.join()

    main()