import requests
from aiogram import types, Router, F
from telegram_bot.methods.buttons import build_inline_markup, build_card_markup
from telegram_bot.methods.responses import text_from_error_response
from variables import bot_dialog
from variables import variables


async def get_catalog() -> [bool, list]:
    url = bot_dialog.categories_url
    response = requests.get(url)
    return await response_validator(response)

async def get_items() -> [bool, list]:
    url = bot_dialog.items_url
    response = requests.get(url)
    return await response_validator(response)

async def response_validator(response, status_code=200) -> [bool, list]:
    if response.status_code == status_code:
        categories = response.json()
        return True, categories['queryset'] if type(categories) is dict else categories
    else:
        error = text_from_error_response(response)
        return False, error

class CatalogView:

    def __init__(self, b_cls):
        self.b_cls = b_cls
        self.router = Router()
        self.register_handlers()
        self.cards_steps = {}

    def register_handlers(self):
        self.router.callback_query.register(self.handle_callback, F.data.startswith(variables.catalog_callback_prefix))
        self.router.callback_query.register(self.handle_callback, F.data.in_(['left', 'right', 'less', 'more', 'to cart']))
        self.router.callback_query.register(self.handle_callback, F.data=='main menu')

    async def handle_callback(self, callback_query: types.CallbackQuery):
        callback_data = callback_query.data
        if variables.catalog_callback_prefix in callback_data:
            catalog_name = callback_data.split(variables.catalog_callback_prefix, 1)[1]
            self.cards_steps[callback_query.message.chat.id][variables.catalog_name] = catalog_name
            await self.show_cards(message=callback_query.message, first=True)

        if callback_data in ['left', 'right', 'less', 'more', 'to cart']:
            match callback_data:
                case'right':
                    next_id_for = self.cards_steps[callback_query.message.chat.id][variables.card_id]
                    await self.show_cards(message=callback_query.message, next_id_for=next_id_for)

        if callback_data == "main menu":
            await self.run_view(message=callback_query.message)


    async def run_view(self, **kwargs):

        is_valid, catalog = await get_catalog()
        if is_valid:
            keyboard = await self.catalog_inline_keyboard(catalog, **kwargs)
            await self.b_cls.bot.send_message(kwargs['message'].chat.id, text=bot_dialog.category_choose, reply_markup=keyboard)
        else:
            await self.b_cls.bot.send_message(kwargs['message'].chat.id, bot_dialog.empty_base)
        pass

    async def catalog_inline_keyboard(self, catalog, **kwargs):
        button_dict = {}
        for item in catalog:
            button_dict[item['name']] = str(f"{variables.catalog_callback_prefix}{item['name']}")
        keyboard, self.b_cls.callbacks[kwargs['message'].chat.id], _ = await build_inline_markup(buttons_dict=button_dict)
        return keyboard

    async def show_cards(self, **kwargs):
        catalog_name = self.cards_steps[kwargs['message'].chat.id][variables.catalog_name]
        next_id_for = kwargs['next_id_for'] if kwargs.get('next_id_for') else None
        if not next_id_for:
            card = await self.get_next_card_for(query_params={variables.category: catalog_name, variables.next_for_id: 0})
        else:
            card = await self.get_next_card_for(query_params={variables.category: catalog_name, variables.next_for_id: next_id_for})

        if card:
            await self.display_card(card_dict=card['queryset'], **kwargs)
        else:
            pass
        pass

    async def get_next_card_for(self, query_params:dict):
        url_query_params = await self.get_query_params_from_dict(query_params)
        url = bot_dialog.items_url + url_query_params
        response = requests.get(url)
        if response.status_code == 200:
            item = response.json()
            return item
        else:
            pass

    async def get_query_params_from_dict(self, query_params):
        url_query_params = "?"
        for key, value in query_params.items():
            url_query_params += f"{key}={value}&"
        return url_query_params[:-1]


    async def display_card(self, card_dict:dict=None, **kwargs):
        first = kwargs['first'] if kwargs.get('first') else False
        last = kwargs['last'] if kwargs.get('last') else False

        self.cards_steps[kwargs['message'].chat.id][variables.card_id] = card_dict['id']

        keyboard_dict = bot_dialog.card_buttons
        keyboard_dict = await self.up_to_date_keybord(keyboard_dict, **kwargs)

        keyboard = await build_card_markup(keyboard_dict)
        caption = await self.card_caption(card_dict)

        if not self.cards_steps[kwargs['message'].chat.id].get(variables.message):
            self.cards_steps[kwargs['message'].chat.id][variables.message] = await self.b_cls.bot.send_photo(chat_id=kwargs['message'].chat.id, photo=card_dict['img_url'], caption=caption, reply_markup=keyboard)
        else:
            message_id = self.cards_steps[kwargs['message'].chat.id][variables.message].message_id
            media = types.InputMediaPhoto(media=card_dict['img_url'], caption=caption)
            self.cards_steps[kwargs['message'].chat.id][variables.message] = await self.b_cls.bot.edit_message_media(chat_id=kwargs['message'].chat.id, message_id=message_id, media=media, reply_markup=keyboard)


    async def set_variables_values(self, **kwargs):
        self.cards_steps[kwargs['message'].chat.id] = {}


    async def card_caption(self, card_dict:dict) -> str:
        caption = ""
        caption += card_dict['name'] + "\n" if card_dict.get('name') else ""
        caption += "Артикул: " + card_dict['article'] + "\n" if card_dict.get('article') else ""
        caption += "Производитель: " + card_dict['manuactured'] + "\n" if card_dict.get('manuactured') else ""
        caption += "Размер: " + card_dict['size'] + "\n" if card_dict.get('size') else ""
        caption += "Состав: " + card_dict['composition'] + "\n" if card_dict.get('composition') else ""
        caption += "Цена: " + card_dict['price'] + "\n" if card_dict.get('price') else ""
        return caption

    async def up_to_date_keybord(self, keyboard_dict: dict, **kwargs) -> dict:
        keyboard_updated = {key: {} for key in keyboard_dict}
        for key in keyboard_dict:
            for button in keyboard_dict[key]:
                if button in bot_dialog.text_empty_to_change_values:
                    if button == bot_dialog.button_number_empty['text']:
                        keyboard_updated[key][button] = await self.change_button_text_to_actual(keyboard_dict, bot_dialog.button_number_empty['text'], **kwargs)
                    elif button == bot_dialog.button_amount_empty['text']:
                        keyboard_updated[key][button] = await self.change_button_text_to_actual(keyboard_dict, bot_dialog.button_amount_empty['text'], **kwargs)
                    else:
                        keyboard_updated[key][button] = keyboard_dict[key][button]
                else:
                    keyboard_updated[key][button] = keyboard_dict[key][button]
        return keyboard_updated

    async def change_button_text_to_actual(self, keyboard_dict, button_text, **kwargs):
        keyboard_updated = keyboard_dict.copy()
        query_param = await self.get_query_params_from_dict({variables.category: self.cards_steps[kwargs['message'].chat.id][variables.catalog_name]})
        url = bot_dialog.items_url + query_param
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json()
            len_items = items['amount']
            key_above = await self.detect_key_above(keyboard_updated, button_text)
            if key_above:
                keys = list(keyboard_updated['1'].keys())
                index = keys.index(button_text)
                keyboard_updated[key_above].pop(button_text)
                keys[index] = str(len_items)
                keyboard_updated[key_above] = dict(zip(keys, keyboard_updated.values()))
            else:
                pass
        else:
            pass
        return keyboard_updated


    async def detect_key_above(self, keyboard_dict, key_under):
        for key, value in keyboard_dict.items():
            if key_under in value:
                return key
        return None

    async def check_shopping_cart(self, item_id, **kwargs):
        chat_id = kwargs['message'].chat.id
