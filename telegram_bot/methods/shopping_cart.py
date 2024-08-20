import copy

import requests
from aiogram import types, Router, F

from telegram_bot.methods.buttons import build_inline_markup
from telegram_bot.methods.catalog import CatalogView
from variables import bot_dialog, variables

class ShoppingCart:

    def __init__(self, b_cls):
        self.b_cls = b_cls
        self.router = Router()
        self.register_handlers()
        self.cards_steps = {}

    def register_handlers(self):
        self.router.callback_query.register(self.handle_callback, F.data==bot_dialog.confirm_callback)

    async def handle_callback(self, callback_query: types.CallbackQuery):
        output_text, shopping_card_items = await self.send_order_to_sales_department(message=callback_query.message)
        await self.b_cls.send_media.send_media_message(
            keyboard=None,
            message=callback_query.message,
            img_url=variables.bird,
            caption=output_text
        )
    #     response = await self.change_shopping_cart_items_status(shopping_card_items, status='confirmed_by_user', message=callback_query.message)
    #
    # async def change_shopping_cart_items_status(self, shopping_card_items, status, **kwargs):
    #     for item in shopping_card_items:
    #         item_id = item['id']
    #         telegram_id = kwargs['message'].chat.id
    #
    #
    #     return []

    async def send_order_to_sales_department(self, **kwargs):
        kwargs['sales_department'] = True
        return await self.display_shopping_cart_list(**kwargs)

    async def display_shopping_cart_list(self, **kwargs):
        shopping_cart_items = await self.b_cls.api.GET_shopping_cart_items_by_user(**kwargs)
        if not kwargs.get('sales_department'):
            output_text = await self.compose_order_list(shopping_cart_items, sales_department=False)
            keyboard, _, _ = await build_inline_markup(bot_dialog.confirm_shopping_cart_buttons)
            return await self.b_cls.send_media.send_media_message(
                keyboard=keyboard,
                message=kwargs['message'],
                img_url=variables.bird,
                caption=output_text
            )
        else:
            return await self.compose_order_list(shopping_cart_items, **kwargs), shopping_cart_items

    async def compose_order_list(self, shopping_cart_items, **kwargs):
        sales_department = kwargs['sales_department'] if kwargs.get('sales_department') else None
        output_text = "КОРЗИНА\n\n" if not sales_department else f"ЗАКАЗ № ХХХ (Это сообщение получает отдел продаж) \n\n{await self.get_user_data(**kwargs)}"
        for item_dict in shopping_cart_items:
            amount = item_dict[variables.amount]
            item_id = item_dict['item']
            item = await self.b_cls.api.GET_item_by_id(item_id)
            if item:
                for key in item:
                    if key in ['name', 'article', 'composition', 'price', 'site_card_item']:
                        output_text += f"{item[key]} | "
                output_text = output_text[:-2] + f"\nКоличество: {amount}\n----------------\n"
            else:
                pass
            pass
        return output_text

    async def get_user_data(self, **kwargs):
        user_portfolio = ""
        telegram_id = kwargs['message'].chat.id
        user = await self.b_cls.api.GET_userId_by_telegramId(telegram_id=telegram_id)
        for key, value in user.items():
            user_portfolio += f"{key}: {value}\n"
        return user_portfolio + "\n\n"

        # shopping_cart_items = await self.b_cls.api.GET_from_cart_by_item_id(**kwargs)
        # if not shopping_cart_items:
        #     keyboard, self.b_cls.callbacks[kwargs['message'].chat.id], _ = await build_inline_markup(bot_dialog.empty_shopping_cart_buttons)
        #     await self.b_cls.send_media.send_media_message(
        #         keyboard=keyboard,
        #         message=kwargs['message'],
        #         img_url=variables.logo,
        #         caption=bot_dialog.empty_shopping_cart
        #     )
        # else:
        #     pass

    async def check_shopping_cart_item(self, **kwargs):
        amount = await self.b_cls.api.Get
