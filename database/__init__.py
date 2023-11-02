from .db_work import Database
from .db_config import SPORT_TYPES



PROMPT_VIEW_GAMES = "SELECT * FROM games;"
PROMPT_VIEW_NO_END_GAMES = "SELECT * FROM games WHERE game_status<>3"
PROMPT_DELETE_GAMES = "TRUNCATE games;"
PROMPT_DELETE_ANSWERS = "TRUNCATE answers;"
PROMPT_RESET_CURRENT_STATISTICS = "UPDATE sports_users_roi SET positive_bets=0, negative_bets=0, roi=0;"
PROMPT_VIEW_USERS_INFO = "SELECT * FROM users;"
PROMPT_INCREASE_NEGATIVE_BETS_POOLE = "UPDATE users SET negative_bets=negative_bets+1 WHERE username='poole';"
PROMPT_CALC_POOLE_ROI = "UPDATE users SET roi=(coeff_sum - positive_bets - negative_bets) / (positive_bets + negative_bets) * 100 WHERE username='poole';"



def get_prompt_recorde_poole(game_key: str,
                             poole_first: int,
                             poole_second: int,
                             poole_draw: int = None) -> str:
    if poole_draw:
        return f"UPDATE games SET poole_first={poole_first}, poole_second={poole_second}, poole_draw={poole_draw} WHERE game_key='{game_key}';"
    else:
        return f"UPDATE games SET poole_first={poole_first}, poole_second={poole_second} WHERE game_key='{game_key}';"
    

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


def get_prompt_view_users_answers(game_key: str) -> str:
    return f"SELECT chat_id, answer FROM answers WHERE game_key='{game_key}';"


def get_prompt_view_users_sport_info(sport_type: str) -> str:
    return f"SELECT * FROM sports_users_roi WHERE sport_type='{sport_type}';"


def get_prompt_view_game_coeffs(game_key: str) -> str:
    return f"SELECT first_coeff, second_coeff, draw_coeff FROM games WHERE game_key='{game_key}';"


def get_prompt_view_username_by_id(chat_id: str) -> str:
    return f"SELECT username FROM users WHERE chat_id='{chat_id}';"


def get_prompt_view_chat_id_by_nick(nickname: str) -> str:
    return f"SELECT chat_id FROM users WHERE nickname='{nickname}';"


def get_prompt_view_nick_by_id(chat_id: str) -> str:
    return f"SELECT nickname FROM users WHERE chat_id='{chat_id}';"


def get_prompts_increase_positive_bets(chat_id: str,
                                       coeff: float,
                                       team: str,
                                       sport_type: str) -> list[str]:
    return [
        f"UPDATE sports_users_roi SET coeff_sum=coeff_sum+{coeff}, positive_bets=positive_bets+1 WHERE chat_id='{chat_id}' AND sport_type='{sport_type}';",
        f"UPDATE users SET coeff_sum=coeff_sum+{coeff}, positive_bets=positive_bets+1 WHERE chat_id='{chat_id}';"
        # f"UPDATE positive_votes_poole SET {team}={team}+1;"
    ]


def get_prompts_increase_negative_bets(chat_id: str,
                                       sport_type: str) -> list[str]:
    return [
        f"UPDATE sports_users_roi SET negative_bets=negative_bets+1 WHERE chat_id='{chat_id}' AND sport_type='{sport_type}';",
        f"UPDATE users SET negative_bets=negative_bets+1 WHERE chat_id='{chat_id}';",
    ]


def get_prompt_increase_positive_bets_poole(coeff: float) -> str:
    return f"UPDATE users SET positive_bets=positive_bets+1, coeff_sum=coeff_sum+{coeff} WHERE username='poole';"


def get_prompt_increase_positive_bets_team(coeff: float,
                                           team_name: str) -> str:
    return f"UPDATE teams SET coeff_sum=coeff_sum+{coeff}, positive_bets=positive_bets+1 WHERE team_name='{team_name}';"


def get_prompt_increase_negative_bets_team(team_name: str) -> str:
    return f"UPDATE teams SET negative_bets=negative_bets+1 WHERE team_name='{team_name}';"


def get_prompts_calculate_roi(chat_id: str,
                              sport_type: str) -> list[str]:
    return [
        f"UPDATE sports_users_roi SET roi=(coeff_sum - positive_bets - negative_bets) / (positive_bets + negative_bets) * 100 WHERE chat_id='{chat_id}' AND sport_type='{sport_type}';",
        f"UPDATE users SET roi=(coeff_sum - positive_bets - negative_bets) / (positive_bets + negative_bets) * 100 WHERE chat_id='{chat_id}';"
    ]


def get_prompt_calculate_teams_roi(team_name: str = None) -> str:
    return f"UPDATE teams SET roi=(coeff_sum - positive_bets - negative_bets) / (positive_bets + negative_bets) * 100 WHERE team_name='{team_name}';"


def get_prompt_view_user_team(chat_id: str) -> str:
    return f"SELECT team_name FROM users WHERE chat_id='{chat_id}';"



__all__ = [
    'Database',
    'SPORT_TYPES',
    'PROMPT_VIEW_GAMES',
    'PROMPT_VIEW_NO_END_GAMES',
    'PROMPT_DELETE_GAMES',
    'PROMPT_DELETE_ANSWERS',
    'PROMPT_RESET_CURRENT_STATISTICS',
    'PROMPT_VIEW_USERS_INFO',
    'PROMPT_INCREASE_NEGATIVE_BETS_POOLE',
    'PROMPT_CALC_POOLE_ROI',
    'get_prompts_increase_positive_bets',
    'get_prompts_increase_negative_bets',
    'get_prompt_increase_positive_bets_poole',
    'get_prompt_increase_positive_bets_team',
    'get_prompt_increase_negative_bets_team',
    'get_prompts_calculate_roi',
    'get_prompt_calculate_teams_roi',
    'get_prompt_recorde_poole',
    'get_prompt_add_game',
    'get_prompt_update_status',
    'get_prompt_view_users_answers',
    'get_prompt_view_game_coeffs',
    'get_prompt_view_username_by_id',
    'get_prompt_view_chat_id_by_nick',
    'get_prompt_view_nick_by_id',
    'get_prompt_view_user_team',
    'get_prompt_view_users_sport_info'
]