import multiprocess as mp

import subprocess
import os
import time

from feed_bot.tg_bot.bin.main import FeedBot

if __name__ == "__main__":

    def start_server():
          
        os.chdir('feed_bot')
        #subprocess.run("daphne -v 0 meta.asgi:application")
        try:
            for app_name in ("tg_bot", "website"):
                subprocess.run(f"python manage.py makemigrations {app_name}")
                subprocess.run(f"python manage.py migrate --database default")
            subprocess.run("python manage.py runserver 0.0.0.0:8000")
        except:
            for app_name in ("tg_bot", "website"):
                subprocess.run(["python", "manage.py", "makemigrations", f"{app_name}"])
                subprocess.run(["python", "manage.py", "migrate", "--database", "default"])
            subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:8000"])
        os.chdir("..")

    def start_bot():
        
        bot = FeedBot()
        bot.run()

    def main():

        server_process = mp.Process(target=start_server, name="server")
        bot_process = mp.Process(target=start_bot, name="bot")

        server_process.start()
        bot_process.start()

        server_process.join()
        bot_process.join()

    main()