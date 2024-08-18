import asyncio

import requests
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from service_apps import config_init
from telegram_bot.methods.buttons import build_inline_markup
# from telegram_bot.methods import registration
from telegram_bot.methods.catalog import get_catalog, get_items, CatalogView
from telegram_bot.methods.registration import Registration
from telegram_bot.methods.responses import text_from_error_response, text_from_dict
from telegram_bot.methods.send_media_message import SendMedia
from telegram_bot.methods.set_commands import set_default_commands
from telegram_bot.methods import catalog
from variables import bot_dialog

class RegistrationStates(StatesGroup):
    name = State()
    email = State()
    phone_number = State()


def bot_init(__token):
    bot = Bot(token=__token)
    dp = Dispatcher(storage=MemoryStorage())
    router = Router()
    dp.include_router(router)
    return bot, dp, router


class ViladoShoppingBot:

    def __init__(self):
        config = config_init.config
        self.token = config["ViladoShoppingBot"]["token"]
        print(config["ViladoShoppingBot"]["name"])
        self.bot, self.dp, self.router = bot_init(self.token)
        self.callbacks = {}
        self.registration = Registration(self)
        self.catalog = CatalogView(self)
        self.send_media = SendMedia(self)
        self.register_routers()
        self.cards_steps = {}

    def register_routers(self):
        self.dp.include_router(self.catalog.router)
        self.dp.include_router(self.registration.router)

    async def handlers(self):
        @self.router.message(RegistrationStates.name)
        async def process_name(message: types.Message, state: FSMContext):
            await state.update_data(name=message.text)
            await state.set_state(RegistrationStates.email.state)
            await message.answer(bot_dialog.FSM_form_ask_email)

        @self.router.message(RegistrationStates.email)
        async def process_age(message: types.Message, state: FSMContext):
            await state.update_data(email=message.text)
            await state.set_state(RegistrationStates.phone_number.state)
            await message.answer(bot_dialog.FSM_form_ask_phone_number)

        @self.router.message(RegistrationStates.phone_number)
        async def process_email(message: types.Message, state: FSMContext):
            await state.update_data(phone_number=message.text)
            user_data = await state.get_data()
            user = {
                "telegram_id": message.chat.id,
                'full_name': user_data['name'],
                'email': user_data['email'],
                'phone_number': user_data['phone_number'],
                'username': '@' + message.from_user.username if message.from_user.username else None
            }
            url = bot_dialog.user_url
            new_user_response = requests.post(url=url, json=user)
            if new_user_response.status_code == 201:
                new_user = new_user_response.json()
                keyboard, self.callbacks[message.chat.id], _ = await build_inline_markup(buttons_dict=bot_dialog.start_answer_buttons)
                await self.bot.send_message(message.chat.id, text=bot_dialog.registration_is_successful+f"\n{text_from_dict(new_user)}", reply_markup=keyboard)
                await self.catalog.set_variables_values(message=message)
            else:
                error = text_from_error_response(response=new_user_response)
                keyboard, self.callbacks[message.chat.id], _ = await build_inline_markup(buttons_dict=bot_dialog.registration_answer_button)
                await self.bot.send_message(message.chat.id, error, reply_markup=keyboard)

        @self.dp.message(CommandStart())
        async def start(message: types.Message):
            status_code, user = await self.registration.check_registration(telegram_id=message.chat.id)
            await self.registration.registration_status_code(status_code=status_code, user=user, message=message)

        @self.router.callback_query(lambda c: c.data == 'registration')
        async def callbacks_registration(callback: types.CallbackQuery, state: FSMContext):
            await state.set_state(RegistrationStates.name.state)
            await callback.message.answer(bot_dialog.FSM_form_ask_name)

        @self.router.message(F.text)
        async def text(message: types.Message):
            pass

        @self.router.message(F.document)
        async def handle_document(message: types.Message):
            pass


        async def on_startup(dp):
            await set_default_commands(dp.bot)


        await self.dp.start_polling(self.bot, on_startup=on_startup)


    async def send_message(self, message, text, **kwargs) -> types.Message:
        disable_web_page_preview = True if kwargs.get('disable_web_page_preview') else False
        parse_mode = kwargs['parse_mode'] if kwargs.get('parse_mode') else 'html'
        disable_notification = True if kwargs.get('disable_notification') else False
        reply_markup = kwargs['reply_markup'] if kwargs.get('reply_markup') else None
        return await self.bot.send_message(
            message.chat.id, text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
            disable_web_page_preview=disable_web_page_preview
        )

if __name__ == '__main__':
    bot = ViladoShoppingBot()
    asyncio.run(bot.handlers())