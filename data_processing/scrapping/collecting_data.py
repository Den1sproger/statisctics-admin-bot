import time
import json
import logging

import requests

from datetime import datetime, timedelta, timezone
from database import (Database,
                      SPORT_TYPES,
                      get_prompt_add_game,
                      PROMPT_VIEW_GAMES)
from .base import Scrapper
from ..sheets_work.games import Games
from ..config import FILEPATH_JSON



class Collection(Scrapper):
    """Class for the parsing a data of the games in the favorites on flashscorekz.com"""

    # types of sports by their code
    SPORTS_ID = {
        'g_1_': 'Футбол',
        'g_3_': 'Баскетбол',
        'g_4_': 'Хоккей'
    }
    IS_THERE_DRAW = {
        'Футбол': True,
        'Баскетбол': False,
        'Хоккей': True
    }
    EMAIL_CELL = 'I3'
    PASSWORD_CELL = 'I4'


    def __init__(self,
                 get_full_data: bool = False,
                 *args, **kwargs) -> None:
        
        super().__init__()
        self.session = requests.Session()
        self.full_data = {}

        ws_games = self.spreadsheet.worksheet(Games.SHEET_NAME)

        # email and password to flashscorekz.com
        if get_full_data:
            self.__email = ws_games.acell(self.EMAIL_CELL).value
            self.__password = ws_games.acell(self.PASSWORD_CELL).value


    def __create_post_request(self,
                              url: str,
                              headers: dict[str],
                              params: dict[str, int],
                              retry: int = 5) -> dict[str]:
        try:
            response = self.session.post(
                url=url, headers=headers, data=params
            )
        except Exception as _ex:
            if retry:
                logging.info(f'retry={retry} => {url}')
                retry -= 1
                time.sleep(5)
                return self.__create_post_request(url, headers, params)
            else:
                raise
        else:
            return response.json()
        

    def log_in(self) -> dict[str]:
        # Authorization in the flashscorekz.com, get id and hash
        headers = {
            'authority': 'lsid.eu',
            'accept': '*/*',
            'origin': 'https://www.flashscorekz.com',
            'referer': 'https://www.flashscorekz.com/',
            'user-agent': self.ua.random
        }
        params = {
            "email": self.__email,
            "password": self.__password,
            "namespace": "flashscore",
            "project": 46
        }
        data = self.__create_post_request(
            url='https://lsid.eu/v3/login', headers=headers, params=params
        )
        del data['r']

        return data


    def get_games(self, id: str, hash: str) -> None:
        # get the dict of keys and type of sport of games in the favourites
        headers = {
            'authority': 'lsid.eu',
            'accept': '*/*',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://www.flashscorekz.com',
            'referer': 'https://www.flashscorekz.com/',
            'user-agent': self.ua.random
        }
        params = '{"loggedIn":{"id":"%s","hash":"%s"},"project":46}' % (id, hash)
        
        data = self.__create_post_request(
            url='https://lsid.eu/v3/getdata', headers=headers, params=params
        )

        keys = list(data['data']['mygames']['data'].keys())

        for key in keys:
            sport_type = self.SPORTS_ID.get(key[:4])
            if key[3] == '_':
                self.full_data[key[4:]] = {'sport': sport_type}
            else:
                self.full_data[key[5:]] = {'sport': sport_type}
    

    def __get_team_names(self, game_id: str) -> list[str]:
        # get the names of teams for the one game
        game_data = self._create_game_request(
            url=f'https://local-ruua.flashscore.ninja/46/x/feed/el_{game_id}'
        )

        names = []
        for i in game_data:
            key = i.split('_')[0]  # Берём первое значение после разделителя _
            value = i.split('_')[-1]  # Берём последнее значение после разделителя _
            if 'PD-FNWC' in key:
                names.append(value)

        length = len(names)
        if length > 2:
            middle_index = length // 2
            first_team = ' '.join(names[:middle_index])
            second_team = ' '.join(names[middle_index:])
            return [first_team, second_team]
        else:
            return names


    def get_coeffs(self, game_id: str,
                   sport_type: str) -> list[float | None]:
        # get the coefficients of teams for the one game
        params = {
            '_hash': 'ope',
            'eventId': game_id,
            'projectId': '46',
            'geoIpCode': 'RU',
            'geoIpSubdivisionCode': 'RUNIZ',
        }
        headers = {
            'accept': '*/*',
            'user-agent': self.ua.random
        }
        response = self.session.get(
            url='https://46.ds.lsapp.eu/pq_graphql', headers=headers, params=params
        )
        data = response.json()
        coefficients = data['data']['findPrematchOddsById']['odds'][0]['odds']
        
        try: cf_1 = float(coefficients[-2]['value'].strip())
        except IndexError: cf_1 = ''

        try: cf_2 = float(coefficients[-1]['value'].strip())
        except IndexError: cf_2 = ''
        
        if self.IS_THERE_DRAW[sport_type]:
            try: cf_draw = float(coefficients[-3]['value'].strip())    # coefficient of draw
            except IndexError: cf_draw = ''

            return [cf_draw, cf_1, cf_2]
        else:
            return [cf_1, cf_2]


    def get_team_coeffs(self):
        # Get the teams and the coefficients of games

        for key, value in self.full_data.items():
            teams = self.__get_team_names(game_id=key)
            coeffs = self.get_coeffs(game_id=key,
                                     sport_type=self.full_data[key]['sport'])
            print(coeffs)
            data = {}

            # coeffs for the teams
            data[teams[0]] = coeffs[-2]
            data[teams[1]] = coeffs[-1]
            
            if len(coeffs) == 3:
                # coeffs for the draw
                data['Ничья'] = coeffs[-3]

            value['coeffs'] = data
            time.sleep(2)


    def get_begin_time(self):
        # get the data and the time of the begin of game
        begin_time: str
        unix_time: int

        for key, value in self.full_data.items():
            unix_time = self._get_data_time(game_id=key, data_key='DC')
            tz = timezone(+timedelta(hours=3))
            begin_time = datetime.fromtimestamp(unix_time, tz).strftime('%Y-%m-%d %H:%M')
            value['begin_time'] = begin_time

            time.sleep(2)


    def get_game_url(self):
        # get the url of the game
        for key, value in self.full_data.items():
            value['url'] = f'https://www.flashscorekz.com/match/{key}/#/match-summary'
    

    def recorde_to_json(self):
        # recorging the full data of games to json file
        path = FILEPATH_JSON
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(self.full_data, file, indent=4, ensure_ascii=False)

    
    def get_games_from_json(self) -> dict[dict[str, int]]:
        # extract full data from json
        path = FILEPATH_JSON
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    

    def write_to_database(self):
        # write the full data to the database        
        db = Database()
        games = db.get_data_list(PROMPT_VIEW_GAMES)
        if not games:
            data = self.get_games_from_json()

            queries = []
            for game, info in data.items():
                queries.append(
                    get_prompt_add_game(
                        game_key=game,
                        sport=info['sport'],
                        begin_time=info['begin_time'],
                        coeffs=info['coeffs'],
                        url=info['url']
                    )
                )
                
            db = Database()
            db.action(*queries)