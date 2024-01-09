from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import Config
from db.database import (
    db_subscribe,
    db_unsubscribe,
    db_is_post
)
from utils.resender import (
    resend_post,
#    edit_post,
    edit_greetings,
    remove_delete_post_keyboard,
    delete_post_messages
)
from keyboard import Buttons


router = Router(name=__name__)


@router.message(
    (F.text.startswith("#post") | (F.caption.startswith("#post"))) &
    (F.chat.id == Config.SUPPORT_CHAT_ID)
)
async def post(message: Message, state: FSMContext):
    text = (
        message.text[5:] if message.text
        else message.caption[5:] if message.caption
        else ""
    )
    await resend_post(message, text)


@router.callback_query(F.data == Buttons.DELETE_POST.value)
async def delete_post(clbck: CallbackQuery):
    await remove_delete_post_keyboard(
        clbck.message.message_id
    )
    print(clbck.message.message_id)
    await delete_post_messages(
        clbck.message.message_id
    )


# @router.message(
#     F.reply_to_message &
#     (F.chat.id == Config.SUPPORT_CHAT_ID)
# )
# async def edit_post(message: Message):
#     post_id = message.reply_to_message.message_id
#     if await db_is_post(post_id):
#         await edit_post(
#             chat_post_id=post_id,
#             message=message
#         )


@router.message(F.text == Buttons.SUBSCRIBE.value)
async def subscribe(message: Message):
    await db_subscribe(message.from_user.id, message.from_user.username)

    await edit_greetings(message, is_subscribed=True)


@router.message(F.text == Buttons.UNSUBSCRIBE.value)
async def unsubscribe(message: Message):
    await db_unsubscribe(message.from_user.id)

    await edit_greetings(message, is_subscribed=False)
