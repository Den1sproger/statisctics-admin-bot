import logging

from database import (Database,
                      PROMPT_VIEW_NO_END_GAMES,
                      PROMPT_INCREASE_NEGATIVE_BETS_POOLE,
                      PROMPT_CALC_POOLE_ROI,
                      get_prompt_view_users_answers,
                      get_prompt_update_status,
                      get_prompt_view_user_team,
                      get_prompts_increase_positive_bets,
                      get_prompts_increase_negative_bets,
                      get_prompts_calculate_roi,
                      get_prompt_increase_positive_bets_poole,
                      get_prompt_increase_positive_bets_team,
                      get_prompt_increase_negative_bets_team,
                      get_prompt_calculate_teams_roi,
                      get_prompt_view_team_size)
from ..sheets_work.games import Games
from ..sheets_work.statistics import Stat_mass, Stat_sport_types
from .base import Scrapper



class Calculate(Scrapper):
    """Full calculate of the all statistics"""

    TEAMS = {
        1: 'first_team',
        2: 'second_team',
        3: 'draw'
    }
    

    def __get_teams_prompts(self, teams_votes: dict,
                            result: int,
                            win_coeff: float) -> list:
        teams_prompts = []
        db = Database()

        for team_name, votes in teams_votes.items():
            current_team_votes = list(votes.values())
            team_size = db.get_data_list(
                get_prompt_view_team_size(team_name)
            )[0]['teammates']
            votes_sum = sum(current_team_votes)

            if (votes_sum == 1) or (votes_sum <= (team_size / 2)):
                continue
            
            if 0 in current_team_votes:
                tv = current_team_votes.copy()
                tv.remove(0)
                
                if tv[0] == tv[1]:
                    continue
            
            positive_votes: int
            negative_votes = []

            for item, count in zip(current_team_votes, (1, 2, 3)):
                if count == result:
                    positive_votes = item
                else:
                    negative_votes.append(item)

            if (positive_votes > negative_votes[0]) and (positive_votes > negative_votes[1]):
                teams_prompts.append(
                    get_prompt_increase_positive_bets_team(win_coeff, team_name)
                )
                teams_prompts.append(
                    get_prompt_calculate_teams_roi(team_name)
                )
                
            elif (positive_votes < negative_votes[0]) or (positive_votes < negative_votes[1]):
                teams_prompts.append(
                    get_prompt_increase_negative_bets_team(team_name)
                )
                teams_prompts.append(
                    get_prompt_calculate_teams_roi(team_name)
                )

        return teams_prompts
    
    
    
    def __get_poole_prompts(self, users_votes: tuple[int],
                            result: int,
                            win_coeff: float) -> list:
        poole_prompts = []
        positive_votes: int
        negative_votes = []

        if 0 in users_votes:
            tv = list(users_votes)
            tv.remove(0)
            if tv[0] == tv[1]:
                return poole_prompts

        for item, count in zip(users_votes, (1, 2, 3)):
            if count == result:
                positive_votes = item
            else:
                negative_votes.append(item)

        if (positive_votes > negative_votes[0]) and (positive_votes > negative_votes[1]):
            poole_prompts = [
                get_prompt_increase_positive_bets_poole(win_coeff),
                PROMPT_CALC_POOLE_ROI
            ]
        elif (positive_votes < negative_votes[0]) or (positive_votes < negative_votes[1]):
            poole_prompts = [
                PROMPT_INCREASE_NEGATIVE_BETS_POOLE,
                PROMPT_CALC_POOLE_ROI
            ]

        return poole_prompts



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
            logging.info(_ex)
            return False
        
        if score_1 > score_2:
            return 1        # the first team win
        elif score_1 < score_2:
            return 2        # the second team win
        else:
            return 3        # draw
        


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

                win_coeff = float(coeffs[result - 1].replace(',', '.'))
                
                users = db.get_data_list(
                    get_prompt_view_users_answers(game_key)
                )
                
                first_team_votes = 0
                second_team_votes = 0
                draw_votes = 0
                teams_votes = {}

                # user statistics
                for user in users:
                    answer = user['answer']
                    if answer == 1:
                        first_team_votes += 1
                    elif answer == 2:
                        second_team_votes += 1
                    else:
                        draw_votes += 1

                    user_team = db.get_data_list(
                        get_prompt_view_user_team(user['chat_id'])
                    )[0]['team_name']

                    if user_team:
                        if user_team not in teams_votes:
                            teams_votes[user_team] = {'first_team': 0, 'second_team': 0, 'draw': 0}

                        if answer == 1:
                            teams_votes[user_team]['first_team'] += 1
                        elif answer == 2:
                            teams_votes[user_team]['second_team'] += 1
                        else:
                            teams_votes[user_team]['draw'] += 1


                    if result == user['answer']:
                        change_bets_count = get_prompts_increase_positive_bets(
                            chat_id=user['chat_id'],
                            coeff=win_coeff,
                            team=self.TEAMS[result],
                            sport_type=game['sport']
                        )
                    else:
                        change_bets_count = get_prompts_increase_negative_bets(
                            chat_id=user['chat_id'],
                            sport_type=game['sport']
                        )
                    prompts += change_bets_count
                    calc_roi = get_prompts_calculate_roi(
                        chat_id=user['chat_id'],
                        sport_type=game['sport']
                    )
                    prompts += calc_roi
                
                # poole statistics
                poole_prompts = self.__get_poole_prompts(
                    users_votes=(first_team_votes, second_team_votes, draw_votes),
                    result=result,
                    win_coeff=win_coeff
                )

                # teams statistics
                teams_prompts = self.__get_teams_prompts(teams_votes, result, win_coeff)

                if prompts:
                    prompts += poole_prompts
                    prompts += teams_prompts
                    db.action(*prompts)

        if no_finished_games:
            sm = Stat_mass()
            sm.update_data()
            sst = Stat_sport_types()
            sst.update_data()