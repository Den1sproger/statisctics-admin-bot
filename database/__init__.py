from .db_work import Database
from .db_config import SPORT_TYPES



PROMPT_VIEW_GAMES = "SELECT game_key, sport, begin_time, first_team, first_coeff, second_team," \
                    f"second_coeff, draw_coeff, url FROM games WHERE game_status=1;"
PROMPT_DELETE_GAMES = "TRUNCATE games;"
PROMPT_DELETE_ANSWERS = "TRUNCATE answers;"
PROMPT_RESET_CURRENT_STATISTICS = "UPDATE currents_users_roi SET positive_bets=0, negative_bets=0, roi=0;"



def get_prompt_add_game(game_key: str,
                        sport: str,
                        begin_time: str,
                        coeffs: dict[str],
                        url: str) -> str:
    keys = list(coeffs.keys())
    team_1 = keys[0]
    team_2 = keys[1]
    coeff_1 = coeffs[team_1]
    coeff_2 = coeffs[team_2]
    
    try: draw_coeff = coeffs['Ничья']
    except KeyError:
        return f'INSERT INTO games (game_key, sport, begin_time, first_team, first_coeff, second_team, second_coeff,' \
            f' url, game_status, poole_first, poole_second) VALUES ("{game_key}", "{sport}", "{begin_time}",' \
            f' "{team_1}", "{coeff_1}", "{team_2}", "{coeff_2}", "{url}", 1, 0, 0);'
    
    return f'INSERT INTO games (game_key, sport, begin_time, first_team, first_coeff, second_team, second_coeff,' \
            f' draw_coeff, url, game_status, poole_first, poole_second, poole_draw) VALUES ("{game_key}", "{sport}", "{begin_time}",' \
            f' "{team_1}", "{coeff_1}", "{team_2}", "{coeff_2}", "{draw_coeff}", "{url}", 1, 0, 0, 0);'


def get_prompt_update_status(game_key: str,
                             status: int) -> str:
    return f"UPDATE games SET game_status={status} WHERE game_key='{game_key}';"


def get_prompt_view_users_by_answer(game_key: str) -> str:
    return f"SELECT chat_id, answer FROM answers WHERE game_key='{game_key}';"


def get_prompt_view_game_coeffs(game_key: str) -> str:
    return f"SELECT first_coeff, second_coeff, draw_coeff FROM games WHERE game_key='{game_key}';"


def get_prompt_view_username_by_id(chat_id: str) -> str:
    return f"SELECT username FROM users WHERE chat_id='{chat_id}';"


def get_prompt_view_chat_id_by_nick(nickname: str) -> str:
    return f"SELECT chat_id FROM users WHERE nickname='{nickname}';"


def get_prompt_view_nick_by_id(chat_id: str) -> str:
    return f"SELECT nickname FROM users WHERE chat_id='{chat_id}';"



__all__ = [
    'Database',
    'SPORT_TYPES',
    'PROMPT_VIEW_GAMES',
    'PROMPT_DELETE_GAMES',
    'PROMPT_DELETE_ANSWERS',
    'PROMPT_RESET_CURRENT_STATISTICS',
    'get_prompt_add_game',
    'get_prompt_update_status',
    'get_prompt_view_users_by_answer',
    'get_prompt_view_game_coeffs',
    'get_prompt_view_username_by_id',
    'get_prompt_view_chat_id_by_nick',
    'get_prompt_view_nick_by_id'
]