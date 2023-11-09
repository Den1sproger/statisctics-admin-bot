import logging
import json

from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, CantInitiateConversation
from aiogram.dispatcher.filters import Command, Text
from data_processing import (Collection,
                             Games,
                             Calculate,
                             FILEPATH_JSON)
from database import (Database,
                      PROMPT_VIEW_GAMES,
                      PROMPT_DELETE_GAMES,
                      PROMPT_DELETE_ANSWERS,
                      get_prompt_update_coeffs,
                      PROMPT_VIEW_USERS_INFO)
from ..bot_config import dp, ADMIN, users_bot
from ..keyboards import (get_ikb_gs_url,
                         confirm_finish_ikb,
                         send_notification_ikb)




@dp.message_handler(Text(equals='📋Заполнить таблицу'), user_id=ADMIN)
@dp.message_handler(Command('fill_table'), user_id=ADMIN)
async def fill_table(message: types.Message) -> None:
    # parsing sport games and recorde to json
    try:
        db = Database()
        games = db.get_data_list(PROMPT_VIEW_GAMES)
        if games:
            await message.answer(f'У вас уже заполнены матчи')
            return
        
        scrapper = Collection(get_full_data=True)
        admin_data = scrapper.log_in()
        scrapper.get_games(id=admin_data['id'], hash=admin_data['hash'])
        scrapper.get_begin_time()
        scrapper.get_game_url()
        scrapper.get_team_coeffs()
        scrapper.recorde_to_json()
        scrapper.session.close()

        # writing data to the googlesheet
        gs = Games(full_data=scrapper.full_data)
        gs.write_data()
    except Exception as _ex:
        logging.error(_ex)
        await message.answer("❌❌Ошибка❌❌")
        return
    
    await message.answer(
        text="Таблица заполнена✅",
        reply_markup=get_ikb_gs_url(
            button_text=gs.SHEET_NAME,
            url=gs.URL
        )
    )




@dp.message_handler(Text(equals='🧹Очистить таблицу'), user_id=ADMIN)
@dp.message_handler(Command('clear_table'), user_id=ADMIN)
async def clear_table(message: types.Message) -> None:
    try:
        gs = Games()
        gs.clear_table()
        db = Database()
        db.action(PROMPT_DELETE_GAMES)
    except FileNotFoundError:
        pass
    except Exception as _ex:
        logging.error(_ex)
        await message.answer("❌❌Ошибка❌❌")
        return
    
    await message.answer(
        text=f"Таблица очищена✅",
        reply_markup=get_ikb_gs_url(
            button_text=gs.SHEET_NAME,
            url=gs.URL
        )
    )




@dp.message_handler(Text(equals='🏀🏐Утвердить матчи'), user_id=ADMIN)
@dp.message_handler(Command('approve_games'), user_id=ADMIN)
async def approve_games(message: types.Message) -> None:
    try:
        gs = Games()
        gs.approve_games()
        parser = Collection()
        parser.write_to_database()
    except Exception as _ex:
        logging.error(_ex)
        await message.answer("❌❌Ошибка❌❌")
        return
    
    await message.answer(
        text=f"Данные утверждены✅\nДля корректной работы ничего не меняйте в таблице",
        reply_markup=send_notification_ikb
    )


@dp.callback_query_handler(lambda callback: callback.data == 'send_start_notification')
async def send_start_notification(callback: types.CallbackQuery) -> None:
    db = Database()
    
    users = db.get_data_list(PROMPT_VIEW_USERS_INFO)

    msg_text='❗️Доступно участие в турнире\nВ разделе "Текущие турниры" выберите свой турнир'
    for user in users:
        try:
            await users_bot.send_message(chat_id=user['chat_id'], text=msg_text)
        except (ChatNotFound, CantInitiateConversation):
            await callback.message.answer(
                f'@{user["username"]} не создал чат с ботом'
            )

    await callback.message.answer('✅Уведомления отправлены пользователям')




@dp.message_handler(Text(equals='📊Запомнить пул'), user_id=ADMIN)
@dp.message_handler(Command('remember_poole'), user_id=ADMIN)
async def remember_poole(message: types.Message) -> None:
    try:
        gs = Games()
        gs.recorde_poole()
    except Exception as _ex:
        logging.error(_ex)
        await message.answer("❌❌Ошибка❌❌")
        return

    await message.answer('Пул обновлен')




@dp.message_handler(Text(equals='🧮Рассчитать результаты'), user_id=ADMIN)
@dp.message_handler(Command('calculate'), user_id=ADMIN)
async def full_calculate(message: types.Message) -> None:
    await message.answer('🧮🧮🧮Рассчитываю...')

    try:
        calc = Calculate()
        calc.check_games()
    except Exception as _ex:
        await message.answer('❌❌Ошибка❌❌')
        logging.info(f'calculate => {_ex}')
        return
    
    await message.answer('✅✅✅Расчет успешно произведен, статистика обновлена')




@dp.message_handler(Text(equals='🔢Обновить коэффициенты'), user_id=ADMIN)
@dp.message_handler(Command('update_coeffs'), user_id=ADMIN)
async def update_coeffs(message: types.Message) -> None:
    try:
        with open(FILEPATH_JSON, 'r', encoding='utf-8') as file:
            games = json.load(file)
        
        if not games:
            await message.answer('❌❌У вас не заполнены матчи')
            return
        
        scrapper = Collection()
        db = Database()

        prompts = []
        for game_key in games:
            coeffs = scrapper.get_coeffs(game_id=game_key,
                                        sport_type=games[game_key]['sport'])
            prompts.append(
                get_prompt_update_coeffs(game_key, coeffs)
            )

            teams = tuple(games[game_key]['coeffs'].keys())
            
            games[game_key]['coeffs'][teams[0]] = coeffs[-2]
            games[game_key]['coeffs'][teams[1]] = coeffs[-1]

            if (len(teams) == 3) and (len(coeffs) == 3):
                games[game_key]['coeffs'][teams[2]] = coeffs[0]

        db.action(*prompts)

        with open(FILEPATH_JSON, 'w', encoding='utf-8') as file:
            json.dump(games, file, indent=4, ensure_ascii=False)
        
        games = Games()
        games.update_coeffs()
    except FileNotFoundError:
        await message.answer('❌❌У вас не заполнены матчи')
        return
    except Exception as _ex:
        await message.answer('❌❌Ошибка❌❌')
        logging.info(f'update coeffs => {_ex}')
        return

    await message.answer('✅Коэффициенты обновлены')




@dp.message_handler(Text(equals='🏁Закончить турнир'), user_id=ADMIN)
@dp.message_handler(Command('finish'), user_id=ADMIN)
async def finish(message: types.Message) -> None:
    await message.answer(
        text='Вы точно хотите завершить турнир?\nДанное действие очистит базы игр',
        reply_markup=confirm_finish_ikb
    )


@dp.callback_query_handler(lambda callback: callback.data == 'confirm_finish')
async def confirm_finish(callback: types.CallbackQuery) -> None:
    try:
        db = Database()
        db.action(
            PROMPT_DELETE_ANSWERS,
            PROMPT_DELETE_GAMES
        )
        games_gs = Games()
        games_gs.clear_table()
        
    except FileNotFoundError:
        pass
    except Exception as _ex:
        logging.error(_ex)
        await callback.message.answer("❌❌Ошибка❌❌")
        return
    
    await callback.message.answer(f'✅Турнир завершен')
    await callback.message.delete()


@dp.callback_query_handler(lambda callback: callback.data == 'not_confirm')
async def delete_confirm_msg(callback: types.CallbackQuery) -> None:
    await callback.message.delete()

