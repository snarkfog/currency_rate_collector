from connector import DbUtils


if __name__ == '__main__':
    util = DbUtils()
    util.connect()
    banks = util.get_banks()
    currencies = util.get_currencies()
    for bank_id, bank_url in banks.values():
        module_name, class_name = util.get_parsers(bank_id)
        parser_obj = getattr(__import__('parsers.' + module_name, fromlist=['']), class_name)
        parser = parser_obj(currencies, bank_url, bank_id)
        rates = parser.get_currency_rate()
        for rate in rates['rate']:
            ins_id = util.set_currency(
                bank_id=bank_id,
                currency_id=rate['currency_id'],
                sale=rate['sale'],
                purchase=rate['purchase']
            )

    util.close()
