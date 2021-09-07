from typing import List

from bs4 import BeautifulSoup
import requests

from parsers.bank import Bank


class KiGroupParser(Bank):
    __URL = 'https://obmenka.od.ua/'
    __BANK_NAME = 'Kit Group'

    def __init__(self, currencies: List, bank_url: str, bank_id: int):
        self.__currencies = {
            element[2]: (element[0], element[1]) for element in currencies
        }
        self.__bank_url = bank_url
        self.__bank_id = bank_id

    def __get_html(self):
        resp = requests.get(self.__bank_url)
        return resp.text

    def get_currency_rate(self):
        currency_rate = {
            'bank_id': self.__bank_id,
            'rate': []
        }

        html = self.__get_html()
        soup = BeautifulSoup(html, 'lxml')

        contents = soup.find_all('li', {'class': 'currencies__block'})
        for line in contents:
            name = line.find('div', {'class': 'currencies__block-name'}).find('a').text.split()[1]
            if not name.upper().endswith('/UAH') or name[:3].lower() not in self.__currencies:
                continue

            currency_id = self.__currencies[name[:3].lower()][0]
            purchase = (
                line.
                find('div', {'class': 'currencies__block-buy'}).
                find('div', {'class': 'currencies__block-num'}).
                text.strip())
            sale = (
                line.
                find('div', {'class': 'currencies__block-sale'}).
                find('div', {'class': 'currencies__block-num'}).
                text.strip()
            )

            currency_rate['rate'].append(
                {
                    'currency_id': currency_id,
                    'purchase': round(float(purchase), 2),
                    'sale': round(float(sale), 2)
                }
            )

        return currency_rate


if __name__ == '__main__':
    from connector import DbUtils
    from pprint import pprint

    db = DbUtils()
    db.connect()
    currencies = db.get_currencies()
    bank_id, bank_name, bank_url = db.get_bank_by_id(4)
    db.close()
    parser = KiGroupParser(currencies, bank_url, bank_id)
    pprint(parser.get_currency_rate())
