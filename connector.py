import psycopg2
from psycopg2 import Error
from os import getenv


class DbUtils:
    def __init__(self, auto_commit=True):
        self.__connection = None
        self.__cursor = None
        self.__is_connected = False
        self.__auto_commit = auto_commit

    def connect(self):
        try:
            self.__connection = psycopg2.connect(
                user='user_pg',
                password='user_pg',
                host='localhost',
                port=5432,
                database='postgres'
            )

            self.__cursor = self.__connection.cursor()
            if self.__auto_commit:
                self.__connection.autocommit = True
            else:
                self.__connection.autocommit = False

            self.__is_connected = True
        except (Exception, Error) as ex:
            self.__is_connected = False
            print('Error while connecting to PostgreSQL', ex)

    def close(self):
        if self.__is_connected:
            self.__cursor.close()
            self.__connection.close()
            self.__is_connected = False

    def test_connection(self):
        if self.__is_connected:
            self.__cursor.execute('select current_timestamp;')
            return self.__cursor.fetchone()

        return 'No connect'

    def get_bank_by_id(self, bank: (int, str) = None):
        sql = f'''select id, full_name, url 
             from currency_statistics.bank 
            where is_enabled is true
              and id = {bank};'''

        self.__cursor.execute(sql)
        return self.__cursor.fetchone()

    def get_bank_by_name(self, bank: str):
        sql = f'''select id, full_name, url
             from currency_statistics.bank 
            where is_enabled is true 
              and full_name = '{bank}';'''

        self.__cursor.execute(sql)
        return self.__cursor.fetchone()

    def get_banks(self):
        sql = f'''select id, full_name, url
             from currency_statistics.bank 
            where is_enabled is true
            order by id;'''

        self.__cursor.execute(sql)
        res_dict = {bank_name: (bank_id, url) for bank_id, bank_name, url in self.__cursor.fetchall()}
        return res_dict

    def get_currency_by_name(self, currency_name: str):
        sql = f'''
            select id, international_name, current_name
            from currency_statistics.currency
            where is_enabled is true
                and lower(current_name) = lower('{currency_name}');
        '''

        self.__cursor.execute(sql)
        return self.__cursor.fetchone()

    def get_currencies(self):
        sql = f'''
            select id, international_name, current_name
            from currency_statistics.currency
            where is_enabled is true;
        '''

        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def set_currency(self, bank_id: int, currency_id: int, sale: float, purchase: float):
        sql = f'''
            insert into currency_statistics.rate (bank_id, currency_id, sale, purchase)
            values ({bank_id}, {currency_id}, {sale}, {purchase})
            returning id;
        '''

        self.__cursor.execute(sql)

        return self.__cursor.fetchone()

    def get_parsers(self, bank_id):
        sql = f'''
            select module_name, class_name
            from currency_statistics.parsers
            where bank_id = {bank_id};
        '''
        self.__cursor.execute(sql)

        return self.__cursor.fetchone()


if __name__ == '__main__':
    db = DbUtils()
    db.connect()
    print(db.get_parsers(1))
    db.close()
