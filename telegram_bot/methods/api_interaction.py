import requests

from variables import variables, bot_dialog
from telegram_bot.methods.catalog import CatalogView


class APIInteraction:
    def __init__(self, b_cls):
        self.b_cls = b_cls

    # Shopping cart Model
    async def GET_from_cart_by_item_id(self, **kwargs):
        telegram_id = kwargs['message'].chat.id
        item_id = self.b_cls.cards_steps[telegram_id][variables.card_id]
        url = bot_dialog.shopping_cart_url
        user = await self.GET_userId_by_telegramId(telegram_id)
        query_params = await CatalogView.get_query_params_from_dict({'user': user['id'], 'item': item_id})
        status_code, shopping_cart_item = await self.GET_request(url=url+query_params)
        return shopping_cart_item

    async def GET_shopping_cart_items_by_user(self, **kwargs):
        url = bot_dialog.shopping_cart_url
        telegram_id = kwargs['message'].chat.id
        user = await self.GET_userId_by_telegramId(telegram_id)
        query_params = await CatalogView.get_query_params_from_dict({'user': user['id']})
        status_code, shopping_cart_item = await self.GET_request(url=url+query_params)
        return shopping_cart_item

    async def POST_shopping_cart(self, **kwargs):
        message = kwargs['message'] if kwargs.get('message') else kwargs['callback_query'].message
        telegram_id = message.chat.id
        item_id = self.b_cls.cards_steps[telegram_id][variables.card_id]
        url = bot_dialog.shopping_cart_url
        amount = self.b_cls.cards_steps[message.chat.id][variables.amount]
        user = await self.GET_userId_by_telegramId(telegram_id)
        body = {
            "user": user['id'],
            "item": item_id,
            "amount": amount
        }
        response = await self.POST_request(url=url, body=body)
        return response

    async def DELETE_from_shopping_cart(self, shopping_cart_instance, **kwargs):
        if type(shopping_cart_instance) is list:
            shopping_cart_instance = shopping_cart_instance[0]
        shopping_cart_id = shopping_cart_instance['id']
        print(shopping_cart_id)
        url = bot_dialog.shopping_cart_url + f"{shopping_cart_id}/"
        response = requests.delete(url)
        return response

    async def PATCH_amount_shopping_cart(self, shopping_cart_instance, **kwargs):
        message = kwargs['message'] if kwargs.get('message') else kwargs['callback_query'].message
        if type(shopping_cart_instance) is list:
            shopping_cart_instance = shopping_cart_instance[0]
        shopping_cart_id = shopping_cart_instance['id']
        print(shopping_cart_id)
        url = bot_dialog.shopping_cart_url + f"{shopping_cart_id}/"
        amount = self.b_cls.cards_steps[message.chat.id][variables.amount]
        body = {
            variables.amount: amount
        }
        response = requests.patch(url, json=body)
        return response


    # User Model
    async def GET_userId_by_telegramId(self, telegram_id):
        url = bot_dialog.user_url
        query_params = await CatalogView.get_query_params_from_dict({'telegram_id': telegram_id})
        response = requests.get(url+query_params)
        if response.status_code == 200:
            user = response.json()
            return user['queryset'] if user.get('queryset') else user

        else:
            pass

    # Items Model
    async def GET_item_by_id(self, item_id):
        query_params = await CatalogView.get_query_params_from_dict({'id': item_id})
        url = bot_dialog.items_url+query_params
        status_code, response = await self.GET_request(url)
        if status_code == 200:
            return response
        else:
            pass


    # get request
    async def GET_request(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json()
            return response.status_code, items
        else:
            return response.status_code, {}

    async def POST_request(self, url, body):
        response = requests.post(url=url, json=body)
        if response.status_code == 201:
            return response.json()
        else:
            pass


