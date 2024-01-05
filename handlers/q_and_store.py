from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from message import shop_message, question_message, question_feedback_message
from keyboard import Buttons, GetBackKeyboard
from utils.resender import resend_question_to_admin, resend_answer_to_user

from config import Config


router = Router(name=__name__)


class Form(StatesGroup):
    awaiting_question = State()


@router.message(F.text == Buttons.SHOP.value)
async def shop(message: Message):
    await message.answer(shop_message, reply_markup=GetBackKeyboard().build())


@router.message(F.text == Buttons.QUESTION.value)
async def ask_question(message: Message, state: FSMContext):
    await message.answer(
        question_message, 
        reply_markup=GetBackKeyboard().build()
    )
    await state.set_state(Form.awaiting_question)


@router.message(Form.awaiting_question)
async def chat_initiation(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if message_count := state_data.get("message_count"):
        await state.update_data(message_count=message_count + 1)
    else:
        await state.update_data(message_count=1)
        
        await message.answer(text=question_feedback_message)
    
    await resend_question_to_admin(message=message)


@router.message((F.chat.id == Config.SUPPORT_CHAT_ID) & F.reply_to_message)
async def support_message_to_user(message: Message, state: FSMContext):
    await resend_answer_to_user(message=message)
