import string

from ..config import Connect
from database import (SPORT_TYPES,
                      Database,
                      PROMPT_VIEW_USERS_INFO,
                      get_prompt_view_users_sport_info)
from googlesheets import SPREADSHEET_ID


    
class Stat_sport_types(Connect):
    """Class for the work with the data in the worksheet with the users and sport types"""

    CELLS_COLS = {
        "chat_id": "A",
        "positive_bets": "B",
        "negative_bets": "C",
        "roi": "D"
    }
    SHEET_NAME = "Стат виды спорта"
    LENGTH = len(CELLS_COLS)
    BETWEEN = 1
    OFFSET = LENGTH + BETWEEN


    def __init__(self, *args, **kwargs):
        super().__init__()
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)
        self.cells = string.ascii_uppercase


    def __get_column(self,
                     column: str,
                     sport_type: str) -> str:
        assert sport_type in SPORT_TYPES, 'Unknown sport type'

        if sport_type == 'Футбол':
            return self.CELLS_COLS[column]
        elif sport_type == 'Хоккей':
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET]
        else:
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET * 2]


    # def reset_stat(self) -> None:
    #     update_data = []
    #     row = len(self.worksheet.col_values(1))
        
    #     for sport_type in SPORT_TYPES:
    #         update_data.append(
    #             {
    #                 f'{self.__get_column("positive_bets", sport_type)}2:{self.__get_column("roi")}{row}',
    #                 [[0, 0, 0]]
    #             }
    #         ) 
    #     self.worksheet.batch_update(update_data)


    def update_data(self):
        db = Database()
        update_data = []

        for sport_type, col_num in zip(SPORT_TYPES, (1, 6, 11)):
            users_chat_id = self.worksheet.col_values(col_num)
            users_info = db.get_data_list(
                get_prompt_view_users_sport_info(sport_type)
            )

            for user in users_info:
                count = users_chat_id.index(user['chat_id']) + 1
                update_data.append({
                    "range": f"{self.CELLS_COLS['positive_bets']}{count}:{self.CELLS_COLS['roi']}{count}",
                    'values': [[
                        user['positive_bets'],
                        user['negative_bets'],
                        user['roi']
                    ]]
                })
                
        self.worksheet.batch_update(update_data)



class Stat_mass(Connect):
    """Class for the work with the data in the worksheet with the all users"""

    CELLS_COLS = {
        "chat_id": "A",
        "username": "B",
        "nickname": "C",
        "positive_bets": "D",
        "negative_bets": "E",
        "roi": "F",
        "coeff_sum": "G"
    }
    SHEET_NAME = "Статы массовые"


    def __init__(self, *args, **kwargs):
        super().__init__()
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)


    def update_data(self):
        users_chat_id = self.worksheet.col_values(1)
        db = Database()
        users_info = db.get_data_list(PROMPT_VIEW_USERS_INFO)
        update_data = []

        for user in users_info:
            count = users_chat_id.index(user['chat_id']) + 1
            update_data.append({
                'range': f"{self.CELLS_COLS['positive_bets']}{count}:{self.CELLS_COLS['coeff_sum']}{count}",
                'values': [[
                    user['positive_bets'],
                    user['negative_bets'],
                    user['roi'],
                    user['coeff_sum']
                ]]
            })

        self.worksheet.batch_update(update_data)

