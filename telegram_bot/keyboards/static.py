from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)


main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton('📋Заполнить таблицу'), KeyboardButton('🧹Очистить таблицу')],
        [KeyboardButton('🏀🏐Утвердить матчи'), KeyboardButton('📊Запомнить пул')],
        [KeyboardButton('🧮Рассчитать результаты'), KeyboardButton('🏁Закончить турнир')],
        [KeyboardButton('🆘Помощь')]
    ]
)

confirm_finish_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('Подтвердить завершение', callback_data='confirm_finish')],
        [InlineKeyboardButton('Не завершать', callback_data='not_confirm')]
    ]
)