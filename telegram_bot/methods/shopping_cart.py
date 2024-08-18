import requests
from aiogram import types, Router, F

from telegram_bot.methods.catalog import CatalogView
from variables import variables, bot_dialog


class ShoppingCart:

    def __init__(self, b_cls):
        self.b_cls = b_cls
        self.router = Router()
        self.register_handlers()
        self.cards_steps = {}

    def register_handlers(self):
        self.router.callback_query.register(self.handle_callback, F.data==bot_dialog.button_to_cart['callback'])

    async def handle_callback(self, callback_query: types.CallbackQuery):
        await self.display_shopping_cart_list(message=callback_query.message)
        pass

    async def display_shopping_cart_list(self, **kwargs):
        query_param = {
            variables.catalog_name: self.b_cls.cards_steps[kwargs['message'].chat.id][variables.catalog_name]
        }
        catalog = CatalogView.get_query_params_from_dict(query_params=)
        shopping_cart_items = requests.get
