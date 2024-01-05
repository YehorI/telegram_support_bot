import logging
from aiogram import F, Router, Dispatcher
from aiogram.types import Message, ReplyKeyboardRemove

import os
import asyncio
import sys

from dotenv import load_dotenv

from aiogram.fsm.context import FSMContext

from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.enums.parse_mode import ParseMode

from keyboard import Buttons, GreetingsKeyboard
from message import greetings_message, support_start_message

from handlers.bonus import router as bonus_router
from handlers.q_and_store import router as q_and_store_router
from handlers.statistics import router as statistics_router

from create_bot import TelegramBot
from db.database import initialize_db, register_unique_user
from config import Config


logging.basicConfig(level=logging.INFO)

bot = TelegramBot().bot

router = Router(name="router")
router.include_routers(
    bonus_router,
    q_and_store_router,
    statistics_router
)
dp = Dispatcher()
dp.include_router(router)


async def show_start_menu(message: Message):
    if message.chat.type == "private":
        await message.answer(
            text=greetings_message, reply_markup=GreetingsKeyboard().build())

        await register_unique_user(
            message.from_user.id,
            message.from_user.username,
        )
    else:
        ...


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await show_start_menu(message)


@router.message(F.text == Buttons.START.value)
async def back_to_menu_handler(message: Message, state: FSMContext):
    await state.clear()
    await show_start_menu(message)


@router.message(Command('help'))
async def show_help(message: Message):
    if message.chat.id == Config.SUPPORT_CHAT_ID:
        await message.answer(
            text=support_start_message,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN
        )


async def on_shutdown(dispatcher: Dispatcher):
    # Close DB connections or clean up sessions
    # If using aiohttp directly:
    await dispatcher.bot.session.close()


async def main() -> None:
    await initialize_db()
    await dp.start_polling(bot, on_shutdown=on_shutdown)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
