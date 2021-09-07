from typing import List

from bs4 import BeautifulSoup
import requests
import re

from parsers.bank import Bank


class OschadBankParser(Bank):
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

        contents = soup.find('div', {'class': 'currency-wrap'}).find_all('div', {
            'class': 'paragraph paragraph--type--exchange-rates paragraph--view-mode--default currency-item'
        })
        for line in contents:
            name = line.find('span', {'class': re.compile('^currency-sign*')}).text.strip().lower()
            if name in self.__currencies.keys():
                currency_id = self.__currencies[name][0]
                purchase = line.find('strong', {'class': re.compile('^buy-*')}).text.strip()
                sale = line.find('strong', {'class': re.compile('^sell-*')}).text.strip()

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
    bank_id, bank_name, bank_url = db.get_bank_by_id(5)
    db.close()
    parser = OschadBankParser(currencies, bank_url, bank_id)
    pprint(parser.get_currency_rate())
