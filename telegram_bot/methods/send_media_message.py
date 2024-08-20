from aiogram import types
from variables import variables, bot_dialog


class SendMedia:
    def __init__(self, b_cls):
        self.b_cls = b_cls

    async def send_media_message(self, **kwargs):
        keyboard = kwargs['keyboard'] if kwargs.get('keyboard') else None
        img_url = kwargs['img_url']
        caption = kwargs['caption']
        if not self.b_cls.cards_steps[kwargs['message'].chat.id].get(variables.message):
            self.b_cls.cards_steps[kwargs['message'].chat.id][variables.message] = await self.b_cls.bot.send_photo(
                chat_id=kwargs['message'].chat.id,
                photo=img_url,
                caption=caption,
                reply_markup=keyboard
            )
        else:
            message_id = self.b_cls.cards_steps[kwargs['message'].chat.id][variables.message].message_id
            try:
                media = types.InputMediaPhoto(media=img_url, caption=caption)
                self.b_cls.cards_steps[kwargs['message'].chat.id][variables.message] = \
                    await self.b_cls.bot.edit_message_media(
                    chat_id=kwargs['message'].chat.id,
                    message_id=message_id, media=media,
                    reply_markup=keyboard
                    )
            except Exception as ex:
                media = types.InputMediaPhoto(media=img_url, caption=str(ex))
                await self.b_cls.bot.edit_message_media(
                    chat_id=kwargs['message'].chat.id,
                    message_id=message_id, media=media,
                    reply_markup=keyboard
                )

