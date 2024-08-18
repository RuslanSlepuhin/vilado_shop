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
        # self.register_handlers()

    # def register_handlers(self):
    #     self.router.callback_query.register(self.handle_callback, F.data=='registration')
    #     self.router.message.register(self.process_name, RegistrationStates.name)
    #     self.router.message.register(self.process_age, RegistrationStates.email)
    #     self.router.message.register(self.process_email, RegistrationStates.phone_number)
    #
    # # @self.router.message(RegistrationStates.name)
    # async def process_name(self, message: types.Message, state: FSMContext):
    #     await state.update_data(name=message.text)
    #     await state.set_state(RegistrationStates.email.state)
    #     await message.answer(bot_dialog.FSM_form_ask_email)
    #
    # # @self.router.message(RegistrationStates.email)
    # async def process_age(self, message: types.Message, state: FSMContext):
    #     await state.update_data(email=message.text)
    #     await state.set_state(RegistrationStates.phone_number.state)
    #     await message.answer(bot_dialog.FSM_form_ask_phone_number)
    #
    # # @self.router.message(RegistrationStates.phone_number)
    # async def process_email(self, message: types.Message, state: FSMContext):
    #     await state.update_data(phone_number=message.text)
    #     user_data = await state.get_data()
    #     user = {
    #         "telegram_id": message.chat.id,
    #         'full_name': user_data['name'],
    #         'email': user_data['email'],
    #         'phone_number': user_data['phone_number'],
    #         'username': '@' + message.from_user.username if message.from_user.username else None
    #     }
    #     url = bot_dialog.user_url
    #     new_user_response = requests.post(url=url, json=user)
    #     if new_user_response.status_code == 201:
    #         new_user = new_user_response.json()
    #         keyboard, self.b_cls.callbacks[message.chat.id], _ = await build_inline_markup(buttons_dict=bot_dialog.start_answer_buttons)
    #         await self.b_cls.bot.send_message(message.chat.id, text=bot_dialog.registration_is_successful+f"\n{text_from_dict(new_user)}", reply_markup=keyboard)
    #     else:
    #         error = text_from_error_response(response=new_user_response)
    #         keyboard, self.b_cls.callbacks[message.chat.id], _ = await build_inline_markup(buttons_dict=bot_dialog.registration_answer_button)
    #         await self.b_cls.bot.send_message(message.chat.id, error, reply_markup=keyboard)
    #
    #
    # async def handle_callback(self, callback_query: types.CallbackQuery, state: FSMContext):
    #     await state.set_state(RegistrationStates.name.state)
    #     await self.b_cls.bot.send_message(callback_query.message.chat.id, bot_dialog.FSM_form_ask_name)

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
                await self.b_cls.bot.send_message(kwargs['message'].chat.id, bot_dialog.registration_is_successful)
                await self.b_cls.catalog.set_variables_values(**kwargs)

                inline_keyboard, self.b_cls.callbacks[kwargs['message'].chat.id], _ = await build_inline_markup(
                    buttons_dict=bot_dialog.start_answer_buttons)
                await self.b_cls.send_message(kwargs['message'], bot_dialog.start_answer, reply_markup=inline_keyboard)
                pass

