import time
import json
import os
import string
import logging

from gspread.exceptions import APIError
from gspread.worksheet import Worksheet
from ..config import Connect, FILEPATH_JSON
from database import SPORT_TYPES
from googlesheets import SPREADSHEET_ID, GAMES_SPREADSHEET_URL



class Games(Connect):
    """Class for the work with the data in the spreadsheet with the games"""
    
    CELLS_COLS = {
        'game_number': 'A',
        'sport': 'B',
        'begin_time': 'C',
        'teams': 'D',
        'coefficients': 'E',
        'url': 'F',
        'poole': 'G'
    }
    SHEET_NAME = 'Матчи'
    URL = GAMES_SPREADSHEET_URL


    def __init__(self,
                 full_data: dict = None,
                 *args, **kwargs) -> None:
        super().__init__(SPREADSHEET_ID)

        self.games_data = full_data
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)
        self.cells = string.ascii_uppercase


    def _combining_cells_in_line(self, length: int, count_gs: int) -> None:
        # combining the required cells in one line
        if length in (2, 3):
            offset = length - 1
        else:
            offset == 0
        
        # columns in which to merge rows
        columns = [
            self.CELLS_COLS['game_number'],
            self.CELLS_COLS['sport'],
            self.CELLS_COLS['begin_time'],
            self.CELLS_COLS['url']
        ]
        for i in columns:
            self.worksheet.merge_cells(
                name=f'{i}{count_gs}:{i}{count_gs + offset}',
                merge_type='MERGE_COLUMNS'
            )


    def write_data(self):
        # write all data to googlesheet
        full_data = []
        formats = []
        count_gs = 2
        count = 1
        for data in list(self.games_data.values()):
            length = len(data['coeffs'])

            self._combining_cells_in_line(length, count_gs)
            time.sleep(1)

            # writing the number of game in table
            column = self.CELLS_COLS["game_number"]
            full_data.append(
                {
                    'range': f'{column}{count_gs}',
                    'values': [[count]]
                }
            )
            formats.append(
                {
                    "range": f"{column}{count_gs}",
                    "format": {
                        "textFormat": {"bold": True},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                }
            )

            # writing the type of sport, the date and time and the link of the game
            for i in ('sport', 'begin_time', 'url'):
                column = self.CELLS_COLS[i]
                full_data.append(
                    {
                        "range": f"{column}{count_gs}",
                        "values": [[data.get(i)]]
                    }
                )
                formats.append(
                    {
                        "range": f"{column}{count_gs}",
                        "format": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"
                        }
                    }
                )

            # writing the teams and the coefficients
            offset = 0
            for team, coeff in data['coeffs'].items():
                full_data.append(
                    {
                        "range": f'{self.CELLS_COLS["teams"]}{count_gs + offset}',
                        "values": [[team, coeff]]
                    }
                )
                offset += 1

            formats.append(
                {
                    "range": f'{self.CELLS_COLS["teams"]}{count_gs}:' \
                             f'{self.CELLS_COLS["coefficients"]}{count_gs + offset}',
                    "format": {"horizontalAlignment": "LEFT"}
                }
            )
            
            count_gs += length
            count += 1

        self.worksheet.batch_update(full_data)
        self.worksheet.batch_format(formats)
        

    def clear_table(self):
        # Clear the table and unmerge the all cells
               
        last_row = len(
            self.worksheet.col_values(
                self.cells.index(self.CELLS_COLS['teams']) + 1
            )
        )
        if last_row < 2:
            last_row = 2
        cells_range = f'{self.CELLS_COLS["game_number"]}2:' \
                        f'{self.CELLS_COLS["url"]}{last_row}'
        self.worksheet.batch_clear([cells_range])
        self.worksheet.unmerge_cells(cells_range)
        
        self.worksheet.format(
            ranges=f"{self.CELLS_COLS['teams']}2:{self.CELLS_COLS['url']}{last_row}",
            format={
                "backgroundColor": {"red": 1.0, "green": 1.0, 'blue': 1.0}
            }
        )

        os.remove(FILEPATH_JSON)


    def approve_games(self):
        # approve the games in table of the games 

        with open(FILEPATH_JSON, 'r', encoding='utf-8') as file:
            games = json.load(file)
        games_data = list(games.values())
        update = False

        getting_data = []
        count = 1
        for game in games_data:
            length = len(game['coeffs'])
            getting_data.append(
                f'{self.CELLS_COLS["sport"]}{count + 1}:{self.CELLS_COLS["url"]}{count + length}'
            )
            count += length
        
        gs_data = self.worksheet.batch_get(getting_data)
    
        count = 2
        for line, game in zip(gs_data, games_data):
            url = line[0][-1]
            if url != game['url']:
                game['url'] = url
                update = True

            for pair, row in zip(game['coeffs'].items(), line):
                length = len(row)
                pair_gs = tuple()

                if length == 3: pair_gs = (row[-1], "")
                elif length == 4: pair_gs = tuple(row[-2:])
                elif length == 5: pair_gs = tuple(row[-3:-1])

                if pair != pair_gs:
                    game['coeffs'][pair_gs[0]] = pair_gs[1]
                    update = True

        if update:
            for i, j in zip(games_data, games):
                games[j] = i

        with open(FILEPATH_JSON, 'w', encoding='utf-8') as file:
            json.dump(games, file, indent=4, ensure_ascii=False)
            

    @staticmethod
    def find_cell(worksheet: Worksheet,
                  query: str,
                  in_column: int,
                  retry: int = 5):
        try:
            cell = worksheet.find(query=query, in_column=in_column)
        except (APIError, Exception) as _ex:
            if retry:
                logging.info(f'retry={retry} => find cell {_ex}')
                retry -= 1
                time.sleep(5)
                return Games.find_cell(
                    worksheet=worksheet, query=query, in_column=in_column, retry=retry
                )
            else:
                raise
        return cell
    

    @staticmethod
    def format_table(worksheet: Worksheet,
                     cells_range: str,
                     format: dict,
                     retry: int = 5) -> None:
        try:
            worksheet.format(ranges=cells_range, format=format)
        except (APIError, Exception) as _ex:
            if retry:
                logging.info(f'retry={retry} => format table {_ex}')
                retry -= 1
                time.sleep(5)
                Games.format_table(
                    worksheet=worksheet, cells_range=cells_range, format=format, retry=retry
                )
            else:
                raise


    def color_cell(self, game_key: str, color: str, winner = None) -> None:
        assert color in ('green', 'red'), 'Unknown color'

        game_url = f'https://www.flashscorekz.com/match/{game_key}/#/match-summary'
        in_column = self.cells.index(self.CELLS_COLS['url']) + 1
        cell = Games.find_cell(
            worksheet=self.worksheet, query=game_url, in_column=in_column
        )
        
        if color == 'green':
            row = cell.row + winner - 1
            ranges = f"{self.CELLS_COLS['teams']}{row}:{self.CELLS_COLS['coefficients']}{row}"
        else:
            ranges = f"{self.CELLS_COLS['url']}{cell.row}"

        Games.format_table(
            worksheet=self.worksheet, cells_range=ranges,
            format={"backgroundColor": {color: 1.0}}
        )