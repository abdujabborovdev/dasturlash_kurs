from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kurs = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Frontend kurs",callback_data="frontend",icon_custom_emoji_id='4985893518061863752')],
    [InlineKeyboardButton(text="Backend kurs",callback_data="backend",icon_custom_emoji_id='4985626654563894116')],
])