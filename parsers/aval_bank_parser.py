import requests
from bs4 import BeautifulSoup
import tabula
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

import time
from typing import List

from parsers.bank import Bank


class RaiffeisenBankAvalParser(Bank):
    def __init__(self, currencies: List, bank_url: str, bank_id: int):
        self.__currencies = {
            element[2]: (element[0], element[1]) for element in currencies
        }
        self.__bank_url = bank_url
        self.__bank_id = bank_id

    def __get_html(self):
        path = 'mac_osx_chromedriver/chromedriver'
        
        display = Display(visible=False, size=(800, 800))
        display.start()

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(path, options=chrome_options)
        driver.get(self.__bank_url)
        count = 0
        html = ''
        while True:
            if count > 60:
                driver.close()
                display.stop()
                return html

            time.sleep(.5)
            try:
                driver.find_element_by_class_name('download-block')
                html = driver.page_source
                driver.close()
                display.stop()
                return html
            except Exception as ex:
                count += 1

    def get_currency_rate(self):
        file_name = 'temp.pdf'
        currency_rate = {
            'bank_id': self.__bank_id,
            'rate': []
        }

        html = self.__get_html()
        if True:
            soup = BeautifulSoup(html, 'lxml')
            file_url = soup.find('div', {'class': 'download-block'}).find('a')['href']
            file_url = 'https://www.aval.ua/' + file_url
            response = requests.get(file_url)
            with open(file_name, 'wb') as file:
                file.write(response.content)

            if os.path.exists(file_name):
                pdf = tabula.read_pdf(file_name, pages=1, output_format="json")
                for line in pdf[0]['data']:
                    i = 0
                    while i < len(line):
                        if line[i]['text'].lower() in self.__currencies:
                            currency_rate['rate'].append(
                                {
                                    'currency_id': self.__currencies[line[i]['text'].lower()][0],
                                    'purchase': round(float(line[i+1]['text']), 2),
                                    'sale': round(float(line[i+2]['text']), 2),
                                }
                            )
                            i += 2
                        else:
                            i += 1

                os.remove(file_name)

        return currency_rate


if __name__ == '__main__':
    from connector import DbUtils
    from pprint import pprint

    db = DbUtils()
    db.connect()
    currencies = db.get_currencies()
    bank_id, bank_name, bank_url = db.get_bank_by_id(2)
    db.close()
    parser = RaiffeisenBankAvalParser(currencies, bank_url, bank_id)
    pprint(parser.get_currency_rate())
