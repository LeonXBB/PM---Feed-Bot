import multiprocess as mp

import subprocess
import os
import time

from feed_bot.tg_bot.bin.main import FeedBot

if __name__ == "__main__":

    def start_server():
          
        root = os.getcwd()
        os.chdir('feed_bot')
        subprocess.run("daphne -v 0 meta.asgi:application")
        os.chdir(root)

    def start_bot():
        
        bot = FeedBot()
        bot.run()

    def main():

        server_process = mp.Process(target=start_server, name="server")
        bot_process = mp.Process(target=start_bot, name="bot")

        server_process.start()
        
        time.sleep(3) # Bot should start after the server
        bot_process.start()

        server_process.join()
        bot_process.join()

    main()