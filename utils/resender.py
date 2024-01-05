from create_bot import TelegramBot
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext

from config import Config
from keyboard import (
    BonusResponseKeyboard,
    BonusResponseHandledKeyboard
)
from db.database import (
    db_save_bonus_request,
    db_get_message_user_id,
    db_add_message
)


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


async def if_bonus_request_already_processed(status, message_id):
    bot = TelegramBot().bot

    await bot.send_message(
        chat_id=Config.SUPPORT_CHAT_ID,
        text=f"Сообщение уже обработано со статусом {status}",
        reply_to_message_id=message_id,
    )


async def resend_question_to_admin(message):
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


async def resend_answer_to_user(message):
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
