import logging

from database import (Database,
                      PROMPT_VIEW_NO_END_GAMES,
                      get_prompt_view_users_answers,
                      get_prompt_update_status,
                      get_prompt_view_user_team,
                      get_prompts_increase_positive_bets,
                      get_prompts_increase_negative_bets,
                      get_prompts_calculate_roi)
from ..sheets_work.games import Games
from ..sheets_work.statistics import Stat_mass, Stat_sport_types
from .base import Scrapper



class Calculate(Scrapper):
    """"""

    TEAMS = {
        1: 'first_team',
        2: 'second_team',
        3: 'draw'
    }


    def check_games(self):
        db = Database()
        no_finished_games = db.get_data_list(PROMPT_VIEW_NO_END_GAMES)

        for game in no_finished_games:
            game_key = game['game_key']
            current_game_status = self._get_data_time(game_key, data_key='DA')
            prompts = []

            if current_game_status == 3:      # if game is over
                prompts.append(               # update game status
                    get_prompt_update_status(game_key, current_game_status)
                )

                result = self.__get_winner(game_key)   # winner

                # color cell
                table_games = Games()
                if not result:
                    table_games.color_cell(game_key=game_key, color='red')
                    continue
                table_games.color_cell(game_key=game_key, color='green', winner=result)
                
                # create list of coeffs
                coeffs = [game['first_coeff'], game['second_coeff']]
                if game['draw_coeff'] != None:
                    coeffs.append(game['draw_coeff'])
                
                users = db.get_data_list(
                    get_prompt_view_users_answers(game_key)
                )

                for user in users:
                    user_team = db.get_data_list(
                        get_prompt_view_user_team(user['chat_id'])
                    )[0]['team_name']

                    if result == user['answer']:
                        win_coeff = coeffs[result - 1]
                        change_bets_count = get_prompts_increase_positive_bets(
                            chat_id=user['chat_id'],
                            coeff=float(win_coeff.replace(',', '.')),
                            team=self.TEAMS[result],
                            sport_type=game['sport'],
                            team_name=user_team
                        )
                    else:
                        change_bets_count = get_prompts_increase_negative_bets(
                            chat_id=user['chat_id'],
                            sport_type=game['sport'],
                            team_name=user_team
                        )
                    prompts += change_bets_count
                    calc_roi = get_prompts_calculate_roi(
                        chat_id=user['chat_id'],
                        sport_type=game['sport'],
                        team_name=user_team
                    )
                    prompts += calc_roi

                if prompts: db.action(*prompts)

        if no_finished_games:
            sm = Stat_mass()
            sm.update_data()
            sst = Stat_sport_types()
            sst.update_data()
        
    
    
    def __get_winner(self, game_id: str) -> int | bool:
        # get the end scores of the teams
        
        data = self._create_game_request(
            url=f'https://local-ruua.flashscore.ninja/46/x/feed/dc_1_{game_id}'
        )
        string = {}
        for item in data:
            key = item.split('÷')[0]
            value = item.split('÷')[-1]
            string[key] = value

        try:
            score_1 = string['DG']
            score_2 = string['DH']
        except Exception as _ex:
            logging.error(_ex)
            return False
        
        if score_1 > score_2:
            return 1        # the first team win
        elif score_1 < score_2:
            return 2        # the second team win
        else:
            return 3        # draw