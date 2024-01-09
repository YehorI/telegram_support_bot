import logging

from create_bot import TelegramBot
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext


from config import Config
from keyboard import (
    BonusResponseKeyboard,
    BonusResponseHandledKeyboard,
    GreetingsKeyboard,
    DeletePostKeyboard
)
from db.database import (
    db_save_bonus_request,
    db_get_message_user_id,
    db_add_message,
    db_get_recipients,
    db_register_post_message,
    db_get_post_messages
)
from message import subscribed_message, unsubscribed_message


async def send_bonus_to_admin(state: FSMContext):
    bot = TelegramBot().bot

    user_data = await state.get_data()

    username = user_data.get('username')
    user_first_name = user_data.get('user_first_name')
    user_last_name = user_data.get('user_last_name')

    screenshot_file_id = user_data.get('screenshot_file_id')
    coupon_file_id = user_data.get('coupon_file_id')
    phone_number = user_data.get('phone_number')

    text = (
        f"Пользователь @{username} ({user_first_name} {user_last_name if user_last_name else ''}) " \
        f"просит засчитать ему бонус\n\n" \
        f"Его номер телефона: `{phone_number}`\n\n" \
        f"{'👇Купон' if coupon_file_id else '(Без купона)'}"
    )

    message = await bot.send_photo(
        chat_id=Config.SUPPORT_CHAT_ID,
        photo=screenshot_file_id,
        caption=text,
    )

    bonus_request_id = await db_save_bonus_request(
        chat_id=user_data.get("chat_id"),
        screenshot_file_id=user_data.get("screenshot_file_id"),
        coupon_file_id=user_data.get("coupon_file_id"),
        phone_number=user_data.get("phone_number"),
        username=user_data.get("username"),
        message_id=message.message_id
    )

    await bot.edit_message_caption(
        caption=f"Номер обращения: #{bonus_request_id}#\n\n{text}",
        chat_id=Config.SUPPORT_CHAT_ID,
        message_id=message.message_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=BonusResponseKeyboard().build()
    )


    if coupon_file_id:
        await bot.send_photo(chat_id=Config.SUPPORT_CHAT_ID, photo=coupon_file_id, caption=f"Купон пользователя @{username}")


async def notify_user_bonus_handled(chat_id, status):
    bot = TelegramBot().bot

    text = (
        "Ваш отзыв обработан администратором.\n" +
        "В ближайшее время вам зачислят бонус!" if status == "accepted"
        else (
            "Кажется что-то не так с предоставленной вами информацией об отзыве.\n\n" \
            "Свяжитесь с поддержкой через функцию бота: 'Задать вопрос' через главное меню."
        )
    )

    await bot.send_message(
        chat_id=chat_id,
        text=text
    )


async def remove_bonus_response_keyboard(message_id, status):
    bot = TelegramBot().bot

    await bot.edit_message_reply_markup(
        chat_id=Config.SUPPORT_CHAT_ID,
        message_id=message_id,
        reply_markup=(
            BonusResponseHandledKeyboard().build_with_condition(
                is_accepted=(
                    True if status == "accepted"
                    else False if status == "declined"
                    else "Error"
                )
            )
        )
    )


async def resend_question_to_admin(message: Message):
    bot = TelegramBot().bot

    message_to_group = await bot.forward_message(
        chat_id=Config.SUPPORT_CHAT_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    await db_add_message(
        user_message_id=message.message_id,
        user_id=message.chat.id,
        support_message_id=message_to_group.message_id
    )


async def resend_answer_to_user(message: Message):
    bot = TelegramBot().bot

    user_id = await db_get_message_user_id(
        support_message_id=message.reply_to_message.message_id
    )

    text = f"*Менеждер поддержки:*\n\n" + message.text

    await bot.send_message(
        chat_id=user_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN
    )


async def resend_post(message: Message, text: str):
    bot = TelegramBot().bot

    await bot.delete_message(
        chat_id=Config.SUPPORT_CHAT_ID,
        message_id=message.message_id
    )
    if message.photo:
        new_message = await bot.send_photo(
            chat_id=Config.SUPPORT_CHAT_ID,
            photo=message.photo[0].file_id,
            caption=text,
            reply_markup=DeletePostKeyboard().build_with_condition(
                is_deleted=False
            )
        )
    else:
        new_message = await bot.send_message(
            chat_id=Config.SUPPORT_CHAT_ID,
            text=text,
            reply_markup=DeletePostKeyboard().build_with_condition(
                is_deleted=False
            )
        )
        print(new_message.message_id)

    subscribers = await db_get_recipients()
    subscriber_ids = [subscriber[0] for subscriber in subscribers]

    for user_id in subscriber_ids:
        try:
            if new_message.photo:
                post_message = await bot.send_photo(
                    chat_id=user_id,
                    photo=new_message.photo[0].file_id,
                    caption=text
                )

            else:
                post_message = await bot.send_message(chat_id=user_id, text=text)
            
            await db_register_post_message(
                chat_post_id=new_message.message_id,
                post_message_id=post_message.message_id,
                post_message_chat_id=user_id
            )

        except Exception as e:
            logging.exception(f"Error sending message to {user_id}: {e}")    


async def remove_delete_post_keyboard(message_id):
    bot = TelegramBot().bot

    await bot.edit_message_reply_markup(
        chat_id=Config.SUPPORT_CHAT_ID,
        message_id=message_id,
        reply_markup=(
            DeletePostKeyboard().build_with_condition(
                is_deleted=True
            )
        )
    )


async def delete_post_messages(chat_post_id):
    bot = TelegramBot().bot

    post_messages = await db_get_post_messages(
        chat_post_id=chat_post_id
     )
    for post_message in post_messages:
        await bot.delete_message(
            chat_id=post_message["chat_id"],
            message_id=post_message["post_id"]
        )

# async def edit_post(chat_post_id, message):
#     post_messages = await db_get_post_messages(chat_post_id)

#     for post_message in post_messages:
#         message_id = post_message["post_id"]
#         chat_id = post_message["chat_id"]

#         await bot.edit_message_text(
#             chat_id=chat_id,
#             message_id=message_id,
#             text=message.text
#         )


async def edit_greetings(message: Message, is_subscribed: bool):
    bot = TelegramBot().bot

    await bot.send_message(
        chat_id=message.chat.id,
        text=subscribed_message if is_subscribed else unsubscribed_message,
        reply_markup=GreetingsKeyboard().build_with_condition(
            is_subscribed=is_subscribed
        )

    )
