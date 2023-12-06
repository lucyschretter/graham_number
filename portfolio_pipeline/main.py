# create portfolio function
'''from util import get_margin_of_safety


def create_portfolio(ticker_list, quarter, year):
    portfolio = []
    for ticker in ticker_list:
        margin = get_margin_of_safety(ticker, quarter, year)
        if margin >= 0:  # > / >= ????!!!
            portfolio.append(ticker)
        else:
            print(f'In {quarter}, {year}, {ticker} is overvalued')

    sorted_portfolio = sorted(portfolio, key=lambda x: x[1], reverse=True)
    return sorted_portfolio'''

from util import get_closing_price
from util import calculate_graham_number
from util import get_reported_date


# get ranked portfolio from graham number price ratio

def create_portfolio(ticker_list, quarter, year):
    portfolio = {}

    for ticker in ticker_list:
        graham_number = calculate_graham_number(ticker, quarter, year)
        date = get_reported_date(ticker, quarter, year)
        price = get_closing_price(ticker, date)
        ratio = graham_number / price

        portfolio[ticker] = ratio

    sorted_portfolio = dict(sorted(portfolio.items(), key=lambda x: x[1], reverse=True))
    return sorted_portfolio


'''tickers = ['AAPL', 'MSFT', 'PEP']

print(main(tickers, 'Q2', '2020'))'''
