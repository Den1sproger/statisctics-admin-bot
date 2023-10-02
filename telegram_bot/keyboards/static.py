from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton('📋Заполнить таблицу'), KeyboardButton('🧹Очистить таблицу')],
        [KeyboardButton('🏀🏐Утвердить матчи'), KeyboardButton('🏁Закончить турнир')],
        [KeyboardButton('🆘Помощь')]
    ]
)