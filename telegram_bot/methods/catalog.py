import copy

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
        # self.cards_steps = {}

    def register_handlers(self):
        self.router.callback_query.register(self.handle_callback, F.data.startswith(variables.catalog_callback_prefix))
        self.router.callback_query.register(self.handle_callback, F.data.in_(bot_dialog.menu_callbacks))
        self.router.callback_query.register(self.handle_callback, F.data=='main menu')

    async def handle_callback(self, callback_query: types.CallbackQuery):
        callback_data = callback_query.data
        self.b_cls.cards_steps[callback_query.message.chat.id][variables.last_callback_value] = callback_data

        if variables.catalog_callback_prefix in callback_data:
            self.b_cls.cards_steps[callback_query.message.chat.id][variables.serial_number] = 1
            catalog_name = callback_data.split(variables.catalog_callback_prefix, 1)[1]
            self.b_cls.cards_steps[callback_query.message.chat.id][variables.catalog_name] = catalog_name
            await self.show_cards(callback_query=callback_query, message=callback_query.message, first=True)

        # elif callback_data in ['left', 'right', 'less', 'more', 'to cart']:
        elif callback_data in bot_dialog.menu_callbacks:
            match callback_data:
                case 'right':
                    self.b_cls.cards_steps[callback_query.message.chat.id][variables.serial_number] += 1
                    next_id_for = self.b_cls.cards_steps[callback_query.message.chat.id][variables.card_id]
                    await self.show_cards(message=callback_query.message, next_id_for=next_id_for)
                case 'left':
                    self.b_cls.cards_steps[callback_query.message.chat.id][variables.serial_number] -= 1
                    previous_id_before = self.b_cls.cards_steps[callback_query.message.chat.id][variables.card_id]
                    await self.show_cards(message=callback_query.message, previous_id_before=previous_id_before)
                case 'add to cart':
                    await self.add_to_cart(callback_query=callback_query, message=callback_query.message)
                case 'show shopping cart':
                    await self.b_cls.shopping_cart.display_shopping_cart_list(message=callback_query.message)
                case 'less':
                    await self.change_card_item_amount(message=callback_query.message, reduce=1)
                case 'more':
                    await self.change_card_item_amount(message=callback_query.message, increase=1)
                case 'less10':
                    await self.change_card_item_amount(message=callback_query.message, reduce=10)
                case 'more10':
                    await self.change_card_item_amount(message=callback_query.message, increase=10)

        elif callback_data == "main menu":
            self.b_cls.cards_steps[callback_query.message.chat.id][variables.serial_number] = 0
            await self.run_view(message=callback_query.message)

    async def add_to_cart(self, **kwargs):
        callback_query = kwargs['callback_query']
        message = callback_query.message
        if self.b_cls.cards_steps[message.chat.id][variables.amount] == 0:
            exists_on_shopping_cart = await self.b_cls.api.GET_from_cart_by_item_id(**kwargs)
            if not exists_on_shopping_cart:

                self.print_cash(**kwargs)

                await self.b_cls.bot.answer_callback_query(
                    callback_query_id=callback_query.id,
                    text=bot_dialog.amount_cannot_be_empty,
                    show_alert=True
                )
            else:
                response = await self.b_cls.api.DELETE_from_shopping_cart(exists_on_shopping_cart, **kwargs)

                self.print_cash(**kwargs)

                await self.b_cls.bot.answer_callback_query(
                    callback_query_id=callback_query.id,
                    text=bot_dialog.item_was_delete_from_shopping_cart,
                    show_alert=False
                )

        else:
            exists_on_shopping_cart = await self.b_cls.api.GET_from_cart_by_item_id(**kwargs)

            self.print_cash(**kwargs)

            if exists_on_shopping_cart:
                response = await self.b_cls.api.PATCH_amount_shopping_cart(exists_on_shopping_cart, **kwargs)
                await self.b_cls.bot.answer_callback_query(
                    callback_query_id=callback_query.id,
                    text=bot_dialog.amount_has_been_updated,
                    show_alert=False
                )

            else:

                self.print_cash(**kwargs)

                response = await self.b_cls.api.POST_shopping_cart(**kwargs)
                if response:
                    await self.b_cls.bot.answer_callback_query(
                        callback_query_id=callback_query.id,
                        text=bot_dialog.items_on_the_cart,
                        show_alert=False
                    )
                self.b_cls.cards_steps[message.chat.id][variables.amount] = 0
            pass

    async def change_card_item_amount(self, **kwargs):
        message = kwargs['message']
        reduce = kwargs['reduce'] if kwargs.get('reduce') else None
        increase = kwargs['increase'] if kwargs.get('increase') else None
        if reduce:
            if self.b_cls.cards_steps[message.chat.id][variables.amount] - reduce < 0:
                if self.b_cls.cards_steps[message.chat.id][variables.amount] == 0:
                    return
                else:
                    self.b_cls.cards_steps[message.chat.id][variables.amount] = 0
            else:
                self.b_cls.cards_steps[message.chat.id][variables.amount] -= reduce
            keyboard = await self.keyboard_change_amount(**kwargs)

        elif increase:
            self.b_cls.cards_steps[message.chat.id][variables.amount] += increase
            keyboard = await self.keyboard_change_amount(**kwargs)


    async def keyboard_change_amount(self, **kwargs):
        keyboard_dict_updated = self.b_cls.cards_steps[kwargs['message'].chat.id][variables.keyboard]
        for key, value in keyboard_dict_updated[bot_dialog.amount_row].items():
            if value == bot_dialog.skip_callback:
                values = list(keyboard_dict_updated[bot_dialog.amount_row].values())
                keys = list(keyboard_dict_updated[bot_dialog.amount_row].keys())
                key_index = keys.index(key)
                keyboard_dict_updated[bot_dialog.amount_row].pop(key)
                keys[key_index] = str(self.b_cls.cards_steps[kwargs['message'].chat.id][variables.amount])
                keyboard_dict_updated[bot_dialog.amount_row] = dict(zip(keys, values))
                break

        keyboard = await build_card_markup(keyboard_dict_updated)
        current_message = self.b_cls.cards_steps[kwargs['message'].chat.id][variables.message]
        self.b_cls.cards_steps[kwargs['message'].chat.id][variables.message] = await self.b_cls.bot.edit_message_reply_markup(chat_id=current_message.chat.id, message_id=current_message.message_id, reply_markup=keyboard)
        pass

    async def run_view(self, **kwargs):

        is_valid, catalog = await get_catalog()
        if is_valid:
            keyboard = await self.catalog_inline_keyboard(catalog, **kwargs)
            await self.b_cls.send_media.send_media_message(
                keyboard=keyboard,
                message=kwargs['message'],
                img_url=variables.logo,
                caption=bot_dialog.category_choose
            )

            # await self.b_cls.bot.send_message(kwargs['message'].chat.id, text=bot_dialog.category_choose, reply_markup=keyboard)
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
        print('show_cards')
        self.b_cls.cards_steps[kwargs['message'].chat.id][variables.amount] = 0
        self.print_cash(**kwargs)
        catalog_name = self.b_cls.cards_steps[kwargs['message'].chat.id][variables.catalog_name]
        next_id_for = kwargs['next_id_for'] if kwargs.get('next_id_for') else None
        previous_id_before = kwargs['previous_id_before'] if kwargs.get('previous_id_before') else None

        if not next_id_for and not previous_id_before:
            card = await self.get_next_card_for(query_params={variables.category: catalog_name, variables.next_for_id: 0})
        elif next_id_for:
            card = await self.get_next_card_for(query_params={variables.category: catalog_name, variables.next_for_id: next_id_for})
        elif previous_id_before:
            card = await self.get_next_card_for(query_params={variables.category: catalog_name, variables.previous_id_before: previous_id_before})
        else:
            card = None

        if card:
            await self.display_card(card_dict=card, **kwargs)
        else:
            callback_left = bot_dialog.button_left['callback']
            callback_right = bot_dialog.button_right['callback']
            if self.b_cls.cards_steps[kwargs['message'].chat.id][variables.last_callback_value] == callback_left:
                card = await self.get_next_card_for(query_params={variables.category: catalog_name, variables.previous_id_before: 0})
                self.b_cls.cards_steps[kwargs['message'].chat.id][variables.serial_number] = card['amount']

            elif self.b_cls.cards_steps[kwargs['message'].chat.id][variables.last_callback_value] == callback_right:
                card = await self.get_next_card_for(query_params={variables.category: catalog_name, variables.next_for_id: 0})
                self.b_cls.cards_steps[kwargs['message'].chat.id][variables.serial_number] = 1

            else:
                card = None
            if card:
                await self.display_card(card_dict=card, **kwargs)
            else:
                await self.b_cls.bot.answer_callback_query(
                    callback_query_id=kwargs['callback_query'].id,
                    text=bot_dialog.have_nothing,
                    show_alert=True
                )

    async def get_next_card_for(self, query_params:dict):
        print('get_next_card_for')
        url_query_params = await self.get_query_params_from_dict(query_params)
        url = bot_dialog.items_url + url_query_params
        response = requests.get(url)
        if response.status_code == 200:
            item = response.json()
            return item
        elif response.status_code == 404:
            return None

    @classmethod
    async def get_query_params_from_dict(cls, query_params):
        print('get_query_params_from_dict')
        url_query_params = "?"
        for key, value in query_params.items():
            url_query_params += f"{key}={value}&"
        return url_query_params[:-1]


    async def display_card(self, card_dict:dict=None, **kwargs):
        print('display_card')
        first = kwargs['first'] if kwargs.get('first') else False
        last = kwargs['last'] if kwargs.get('last') else False

        amount = card_dict['amount']
        card_dict = card_dict['queryset']

        self.b_cls.cards_steps[kwargs['message'].chat.id][variables.card_id] = card_dict['id']

        keyboard_dict = copy.deepcopy(bot_dialog.card_buttons)
        keyboard_dict_updated = await self.up_to_date_keyboard(keyboard_dict, amount, **kwargs)

        self.b_cls.cards_steps[kwargs['message'].chat.id][variables.keyboard] = keyboard_dict_updated

        keyboard = await build_card_markup(keyboard_dict_updated)
        caption = await self.card_caption(card_dict, **kwargs)

        await self.b_cls.send_media.send_media_message(
            keyboard=keyboard,
            message=kwargs['message'],
            img_url=card_dict['img_url'],
            caption=caption
        )
        keyboard_dict = {}

    async def set_variables_values(self, **kwargs):
        self.b_cls.cards_steps[kwargs['message'].chat.id] = {}


    async def card_caption(self, card_dict:dict, **kwargs) -> str:
        caption = self.b_cls.cards_steps[kwargs['message'].chat.id][variables.catalog_name] + "\n\n"
        caption += card_dict['name'] + "\n" if card_dict.get('name') else ""
        caption += "Артикул: " + card_dict['article'] + "\n" if card_dict.get('article') else ""
        caption += "Производитель: " + card_dict['manuactured'] + "\n" if card_dict.get('manuactured') else ""
        caption += "Размер: " + card_dict['size'] + "\n" if card_dict.get('size') else ""
        caption += "Состав: " + card_dict['composition'] + "\n" if card_dict.get('composition') else ""
        caption += "Цена: " + card_dict['price'] + "\n" if card_dict.get('price') else ""
        return caption

    async def up_to_date_keyboard(self, keyboard_dict: dict, amount, **kwargs) -> dict:
        callback_value = None
        print('up_to_date_keyboard')
        keyboard_updated = {key: {} for key in keyboard_dict}
        for key in keyboard_dict:
            for button in list(keyboard_dict[key].keys()):
                if button in bot_dialog.text_empty_to_change_values:
                    if button == bot_dialog.button_number_empty['text']:
                        new_key, callback_value = await self.change_button_text_to_actual(keyboard_dict, amount, bot_dialog.button_number_empty['text'], **kwargs)
                        pass
                        keyboard_updated[key][new_key] = callback_value
                    elif button == bot_dialog.button_amount_empty['text']:
                        new_key = await self.b_cls.api.GET_from_cart_by_item_id(**kwargs)
                        if new_key:
                            new_key = new_key[0]
                            new_key = new_key[variables.amount]
                            self.b_cls.cards_steps[kwargs['message'].chat.id][variables.amount] = new_key
                        else:
                            new_key = '0'
                            self.b_cls.cards_steps[kwargs['message'].chat.id][variables.amount] = 0
                        keyboard_updated[key][str(new_key)] = callback_value
                    else:
                        keyboard_updated[key][button] = keyboard_dict[key][button]
                else:
                    keyboard_updated[key][button] = keyboard_dict[key][button]
        return keyboard_updated

    async def change_button_text_to_actual(self, keyboard_dict, amount, button_text, **kwargs) -> [str, dict]:
        print('change_button_text_to_actual')
        keyboard_updated = keyboard_dict.copy()
        if not amount:
            query_param = await self.get_query_params_from_dict({variables.category: self.b_cls.cards_steps[kwargs['message'].chat.id][variables.catalog_name]})
            url = bot_dialog.items_url + query_param
            response = requests.get(url)
            if response.status_code == 200:
                items = response.json()
                amount = str(items['amount'])
            else:
                pass

        key_above = await self.detect_key_above(keyboard_updated, button_text)
        values = list(keyboard_updated[key_above].values())
        if key_above:
            keys = list(keyboard_updated[key_above].keys())
            index = keys.index(button_text)
            keyboard_updated[key_above].pop(button_text)

            keys[index] = f"{self.b_cls.cards_steps[kwargs['message'].chat.id][variables.serial_number]}/{amount}"
            keyboard_updated[key_above] = dict(zip(keys, values))
            return keys[index], keyboard_updated[key_above][keys[index]]

        else:
            pass


    async def detect_key_above(self, keyboard_dict, key_under):
        for key, value in keyboard_dict.items():
            if key_under in value:
                return key
        return None

    async def check_shopping_cart(self, item_id, **kwargs):
        chat_id = kwargs['message'].chat.id

    def print_cash(self, **kwargs):
        for key, value in self.b_cls.cards_steps[kwargs['message'].chat.id].items():
            if key not in ['keyboard', 'message']:
                print(f"{key} -> {value}")
        print('------------')
