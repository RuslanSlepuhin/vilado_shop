import asyncio
import subprocess
from multiprocessing import Process

from parser_vilado_site_items.parser import ViladoParser
from telegram_bot.main_handlers import ViladoShoppingBot

def start_vilado_bot():
    bot = ViladoShoppingBot()
    asyncio.run(bot.handlers())

def start_django_server():
    command = 'python ViladoAPI//manage.py runserver 8000'
    process = subprocess.Popen(command, shell=True)
    process.communicate()


if __name__ == "__main__":

    p1 = Process(target=start_vilado_bot, args=())
    p2 = Process(target=start_django_server, args=())

    p1.start()
    p2.start()

    p1.join()
    p2.join()
