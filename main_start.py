import asyncio

from parser_vilado_site_items.parser import ViladoParser
from telegram_bot.main_handlers import ViladoShoppingBot

if __name__ == "__main__":
    bot = ViladoShoppingBot()
    asyncio.run(bot.handlers())

    # p = ViladoParser()
    # browser = asyncio.run(p.get_items_from_Vilado())
    # pass
