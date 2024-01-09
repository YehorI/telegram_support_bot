from aiogram import Router, F
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from message import (
    bonus_message,
    screenshot_instructions_message,

    screenshot_failure_message,
    screenshot_success_message,

    coupon_failure_message,
    coupon_success_message,

    thanks_for_info_message,
    number_failure_message
)
from keyboard import (
    Buttons,
    BonusKeyboard,
    GetBackKeyboard,
    SkipCouponKeyboard
)
from utils.resender import (
    send_bonus_to_admin,
    notify_user_bonus_handled,
    remove_bonus_response_keyboard
)
from utils.phone_parser import validate_and_format_number
from db.database import (
    db_get_bonus_request_status,
    db_accept_decline_bonus,
    db_get_user_chatid_by_support_message_id
)


router = Router(name=__name__)


class Form(StatesGroup):
    awaiting_screenshot = State()
    awaiting_coupon = State()
    awaiting_number = State()
    awaiting_bonus_confirmation = State()
    bonus_handled = State()


@router.message(F.text == Buttons.BONUS.value)
async def bonus(message: Message):
    await message.answer(bonus_message, reply_markup=BonusKeyboard().build())


@router.message(F.text == Buttons.SCREENSHOT_INSTRUCTIONS.value)
async def screenshot_instructions(message: Message, state: FSMContext):
    await message.answer(
        screenshot_instructions_message,
        reply_markup=GetBackKeyboard().build()
    )
    await state.update_data(
        username=message.from_user.username,
        user_first_name=message.from_user.first_name,
        user_last_name=message.from_user.last_name,
        chat_id=message.chat.id
    )
    await state.set_state(Form.awaiting_screenshot)



@router.message(Form.awaiting_screenshot)
async def handle_screenshot(message: Message, state: FSMContext):
    if message.content_type == ContentType.PHOTO:

        screenshot_file_id = message.photo[-1].file_id
        await state.update_data(screenshot_file_id=screenshot_file_id)

        await message.answer(
            text=screenshot_success_message,
            reply_markup=SkipCouponKeyboard().build()
        )
        await state.set_state(Form.awaiting_coupon)
    else:
        await message.answer(
            text=screenshot_failure_message,
            reply_markup=GetBackKeyboard().build()
        )


@router.message(Form.awaiting_coupon)
async def handle_coupon(message: Message, state: FSMContext):
    if message.content_type == ContentType.PHOTO:

        coupon_file_id = message.photo[-1].file_id
        await state.update_data(coupon_file_id=coupon_file_id)

        await message.answer(
            text=coupon_success_message,
            reply_markup=GetBackKeyboard().build()
        )

        await state.set_state(Form.awaiting_number)
    elif message.text == Buttons.SKIP_COUPON.value:

        await message.answer(
            text=coupon_success_message,
            reply_markup=GetBackKeyboard().build()
        )
        
        await state.set_state(Form.awaiting_number)

    else:
        await message.answer(text=coupon_failure_message,
            reply_markup=SkipCouponKeyboard().build()
        )


@router.message(Form.awaiting_number)
async def handle_number(message: Message, state: FSMContext):
    phone_number = message.text

    if phone_number := validate_and_format_number(phone_number):
        await state.update_data(phone_number=phone_number)

        user_data = await state.get_data()

        await message.answer(
            text=thanks_for_info_message,
            reply_markup=GetBackKeyboard().build()
        )

        await send_bonus_to_admin(state)
        await state.clear()
    else:
        await message.answer(
            text=number_failure_message,
            reply_markup=GetBackKeyboard().build()
        )


@router.callback_query(F.data.in_({Buttons.ACCEPT_BONUS.value, Buttons.DECLINE_BONUS.value}))
async def accept_decline_bonus(clbck: CallbackQuery):
    this_message_id = clbck.message.message_id

    new_status = (
        "accepted" if clbck.data == Buttons.ACCEPT_BONUS.value \
        else "declined"
)
    await db_accept_decline_bonus(
        this_message_id, new_status
    )
    user_chat_id = await db_get_user_chatid_by_support_message_id(
        message_id=this_message_id
    )
    await remove_bonus_response_keyboard(
        message_id=this_message_id,
        status=new_status,
    )
    await notify_user_bonus_handled(
        chat_id=user_chat_id,
        status=new_status,
    )
