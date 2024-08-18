from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def build_inline_markup(buttons_dict:dict) -> [InlineKeyboardMarkup, list, list]:
    buttons = []
    markup = InlineKeyboardBuilder()
    # buttons = [InlineKeyboardButton(text=key, callback_data=buttons_dict[key]) for key in buttons_dict]
    for key in buttons_dict:
        buttons.append(InlineKeyboardButton(text=key, callback_data=buttons_dict[key]))
    markup.row(*buttons)
    inline_keyboard = [[button] for button in markup.buttons]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard), list(buttons_dict.values()), inline_keyboard

async def build_card_markup(buttons_dict: dict) -> InlineKeyboardMarkup:
    row = []
    markup = InlineKeyboardBuilder()
    for row_buttons in buttons_dict.values():
        # for text, callback_data in row_buttons.items():
        #     try:
        #         row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        #     except Exception as ex:
        #         print(ex)
        #         print(text, callback_data)
        #         pass
        row = [InlineKeyboardButton(text=text, callback_data=callback_data) for text, callback_data in row_buttons.items()]
        markup.row(*row)
    return markup.as_markup()
