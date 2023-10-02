from .db_work import Database
from .db_config import SPORT_TYPES


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

__all__ = [
    'Database',
    'SPORT_TYPES',
    'get_prompt_add_game'
]