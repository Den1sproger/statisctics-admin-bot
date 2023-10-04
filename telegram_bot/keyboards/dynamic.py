from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def get_ikb_gs_url(button_text: str, url: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(button_text, url=url)]
        ]
    )
    return ikb