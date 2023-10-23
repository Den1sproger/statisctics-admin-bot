import string

from ..config import Connect
from database import (SPORT_TYPES,
                      Database)
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


    def reset_stat(self) -> None:
        update_data = []
        row = len(self.worksheet.col_values(1))
        
        for sport_type in SPORT_TYPES:
            update_data.append(
                {
                    f'{self.__get_column("positive_bets", sport_type)}2:{self.__get_column("roi")}{row}',
                    [[0, 0, 0]]
                }
            ) 
        self.worksheet.batch_update(update_data)