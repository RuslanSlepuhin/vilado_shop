import asyncio

import requests
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from telegram_bot.methods.responses import text_from_error_response, text_from_dict
from telegram_bot.methods.buttons import build_inline_markup
from variables import bot_dialog, variables

class RegistrationStates(StatesGroup):
    name = State()
    email = State()
    phone_number = State()

class Registration:
    def __init__(self, b_cls):
        self.b_cls = b_cls
        self.router = Router()

    @classmethod
    async def check_registration(cls, telegram_id) -> [int, dict]:
        url = f"{bot_dialog.user_url}?telegram_id={telegram_id}"
        response = requests.get(url)
        if response.status_code == 200:
            user = response.json()
            if user:
                return response.status_code, user
            else:
                return response.status_code, {}
        return response.status_code, {}

    async def registration_status_code(self, **kwargs):
        """
        :param kwargs:
            message:types.Message,
            user:dict,
            status_code:int
        """
        match kwargs['status_code']:
            case 404:
                keyboard, self.b_cls.callbacks[kwargs['message'].chat.id], _ = await build_inline_markup(
                    buttons_dict=bot_dialog.registration_answer_button)
                await self.b_cls.bot.send_message(kwargs['message'].chat.id, bot_dialog.user_doesnt_have_registration,
                                            reply_markup=keyboard)
            case 500:
                await self.b_cls.bot.send_message(kwargs['message'].chat.id, bot_dialog.server_is_not_response)
            case 200:
                await self.b_cls.catalog.set_variables_values(**kwargs)
                await self.b_cls.send_media.send_media_message(
                    img_url=variables.logo,
                    caption=bot_dialog.registration_is_successful,
                    message=kwargs['message']
                )
                await asyncio.sleep(1)
                # await self.b_cls.bot.send_message(kwargs['message'].chat.id, bot_dialog.registration_is_successful)

                inline_keyboard, self.b_cls.callbacks[kwargs['message'].chat.id], _ = await build_inline_markup(
                    buttons_dict=bot_dialog.start_answer_buttons)
                await self.b_cls.send_media.send_media_message(
                    keyboard=inline_keyboard,
                    message=kwargs['message'],
                    img_url=variables.logo,
                    caption=bot_dialog.start_answer
                )
                pass

