from collections import OrderedDict
from enum import Enum

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class Buttons(Enum):
    QUESTION = "💌 Задать вопрос"
    SHOP = "📍 Наш магазин"
    BONUS = "🎁 Бонус за отзыв"
    START = "🌐 Вернуться в главное меню"
    SCREENSHOT_INSTRUCTIONS = "✅ Я оставил(-а) отзыв"
    SKIP_COUPON = "⏩ Без купона"
    ACCEPT_BONUS = "✅ Принять"
    DECLINE_BONUS = "❌ Отклонить"
    BONUS_ALREADY_ACCEPTED = "👍 Принято"
    BONUS_ALREADY_DECLINED = "👎 Отклонено"
    PLACEHOLDER = "Я PLACEHOLDER"


class BaseReplyKeyboard:
    def build(self, buttons):
        builder = ReplyKeyboardBuilder()
        for button in buttons:
            builder.button(text=button.value)
        return builder.as_markup(resize_keyboard=True)


class BaseInlineKeyboard:
    def build(self, buttons, callback_data_list):
        builder = InlineKeyboardBuilder()
        for button, callback_data in zip(buttons, callback_data_list):
            builder.button(text=button.value, callback_data=callback_data.value)
        return builder.as_markup(resize_keyboard=True)


class GreetingsKeyboard(BaseReplyKeyboard):
    def build(self):
        buttons = [Buttons.QUESTION, Buttons.SHOP, Buttons.BONUS]
        return super().build(buttons)


class BonusKeyboard(BaseReplyKeyboard):
    def build(self):
        buttons = [Buttons.SCREENSHOT_INSTRUCTIONS, Buttons.START]
        return super().build(buttons)


class GetBackKeyboard(BaseReplyKeyboard):
    def build(self):
        buttons = [Buttons.START]
        return super().build(buttons)


class SkipCouponKeyboard(BaseReplyKeyboard):
    def build(self):
        buttons = [Buttons.SKIP_COUPON, Buttons.START]
        return super().build(buttons)


class BonusResponseKeyboard(BaseInlineKeyboard):
    def build(self):
        buttons = [Buttons.ACCEPT_BONUS, Buttons.DECLINE_BONUS]
        callback_data_list = [Buttons.ACCEPT_BONUS, Buttons.DECLINE_BONUS]
        return super().build(buttons, callback_data_list)


class BonusResponseHandledKeyboard(BaseInlineKeyboard):
    """special"""
    def build_with_condition(self, is_accepted: bool):
        buttons = [
            (
                Buttons.BONUS_ALREADY_ACCEPTED if is_accepted
                else Buttons.BONUS_ALREADY_DECLINED
            )
        ]
        return super().build(buttons, [Buttons.PLACEHOLDER for i in buttons])