from bs4 import BeautifulSoup
import requests

import re
from typing import List

from parsers.bank import Bank


class UkrSibBankParser(Bank):
    def __init__(self, currencies: List, bank_url: str, bank_id: int):
        self.__currencies = {
            element[2]: (element[0], element[1]) for element in currencies
        }

        self.__url = bank_url
        self.__bank_id = bank_id

    def __get_html(self):
        resp = requests.get(self.__url)
        return resp.text

    def get_currency_rate(self):
        currency_rate = {
            'bank_id': self.__bank_id,
            'rate': []
        }

        html = self.__get_html()
        soup = BeautifulSoup(html, 'lxml')

        contents = soup.find_all('div', id=re.compile('^NAL*'))
        for line in contents:
            currency_id = None
            for key, value in self.__currencies.items():
                if key.lower() in line['id'].lower():
                    currency_id = value[0]

            if currency_id is None:
                continue

            currency_rate['rate'].append(
                {
                    'currency_id': currency_id,
                    'purchase': round(float(line.find('div', class_='rate__buy').find('p').text.strip('\n').strip()), 2),
                    'sale': round(float(line.find('div', class_='rate__sale').find('p').text.strip('\n').strip()), 2)
                }
            )

        return currency_rate


if __name__ == '__main__':
    from connector import DbUtils
    from pprint import pprint
    db = DbUtils()
    db.connect()
    currencies = db.get_currencies()
    bank_id, bank_name, bank_url = db.get_bank_by_id(3)
    db.close()
    parser = UkrSibBankParser(currencies, bank_url, bank_id)
    pprint(parser.get_currency_rate())
