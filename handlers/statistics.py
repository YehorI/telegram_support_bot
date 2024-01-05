from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from config import Config

from db.database import db_get_bonus_request_stats, db_get_id_and_request_date
from utils.date_parser import parse_dates


router = Router(name=__name__)


@router.message(Command('stat'))
async def get_stats(message: Message, state: FSMContext):
    if message.chat.id == Config.SUPPORT_CHAT_ID:
        text = message.text[5:].strip()

        try:
            dates = parse_dates(text)
        except ValueError:
            await message.answer(
                text="Некорректная дата",
            )
            return

        stats = await db_get_bonus_request_stats(
            start_date=dates[0],
            end_date=dates[1]
        )
        max_min_dates = (datetime(1999, 1, 1), datetime(2999, 1, 1))
        period = (
            f"""{(
                'За все время' if dates == max_min_dates
                else " — ".join((dt.strftime("%d.%m.%y") for dt in dates))
        )}"""
        )

        ids_of_pending = await db_get_id_and_request_date()

        answer_text = (  
            f"Период: {period}\n"
            f"{stats['total_unique_users']}"
            " — уникальных пользователей\n"
            f"{stats['total_unique_requesters']} ({stats['unique_requester_user_ratio']}%)"
            " — пользователей обратившихся за бонусом\n\n"
            "Необработанные заявки (ID): "
            f"{', '.join(f'`{id_[0]}`' for id_ in ids_of_pending) if ids_of_pending else 'нет'}"

            # "Всего обращений за бонусом: "
            # f"{stats['total_requests']}\n"

            # "Обработанных: "
            # f"{stats['processed']}\n"

            # "Необработанных: "
            # f"{stats['pending']}\n\n"

            # "Из них одобренных: "
            # f"{stats['accepted']}\n"

            # "Отклоненных: "
            # f"{stats['declined']}"
        )

        await message.answer(
            text=answer_text,
            parse_mode=ParseMode.MARKDOWN
        )
