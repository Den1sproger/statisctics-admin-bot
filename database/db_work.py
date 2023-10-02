import logging
import time

import pymysql

from .db_config import *



class Database:
    """The class responsible for working with the database of the games and the users"""

    def connect_to_db(self, retry: int = 5) -> pymysql.connect:
        # Connect to the database
        try:
            connection = pymysql.connect(
                host=host, user=user, port=3306,
                password=password, database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Exception as _ex:
            if retry:
                logging.info(f'retry={retry} => {_ex}')
                retry -= 1
                time.sleep(5)
                return self.connect_to_db(retry)
            else:
                raise


    def action(self, *queries) -> None:
        connection = self.connect_to_db()

        with connection:
            with connection.cursor() as cursor:
                for query in queries:
                    try:
                        cursor.execute(query)
                    except pymysql.err.IntegrityError:
                        connection.rollback()
            connection.commit()


    def get_data_list(self, query: str) -> list[str]:
        connection = self.connect_to_db()
            
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
        
        return data
    

    def __del__(self) -> None:
        return