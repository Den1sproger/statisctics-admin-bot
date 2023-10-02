from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from ..bot_config import dp, ADMIN



@dp.message_handler(Text(equals='📋Заполнить таблицу'), user_id=ADMIN)
@dp.message_handler(Command('fill_table'), user_id=ADMIN)
async def fill_table(message: types.Message) -> None:
    pass



@dp.message_handler(Text(equals='🧹Очистить таблицу'), user_id=ADMIN)
@dp.message_handler(Command('clear_table'), user_id=ADMIN)
async def clear_table(message: types.Message) -> None:
    pass



@dp.message_handler(Text(equals='🏀🏐Утвердить матчи'), user_id=ADMIN)
@dp.message_handler(Command('approve_games'), user_id=ADMIN)
async def approve_games(message: types.Message) -> None:
    pass



@dp.message_handler(Text(equals='🏁Закончить турнир'), user_id=ADMIN)
@dp.message_handler(Command('finish'), user_id=ADMIN)
async def finish(message: types.Message) -> None:
    pass


