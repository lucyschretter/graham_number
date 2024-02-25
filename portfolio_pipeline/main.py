from util import get_closing_price
from util import get_reported_date
from util import calculate_gn_with_avg_eps
from util import calculate_acceptable_price


# get ranked portfolio from graham number price ratio

# this function to calculate correctly: price < graham number (sorted by margin of safety)
# from util import get_margin_of_safety


def create_portfolio(ticker_list, quarter_end_date):
    portfolio = {}
    for ticker in ticker_list:
        try:
            # graham_number = calculate_gn_with_avg_eps(ticker, quarter_end_date)
            # print(f"Graham number for {ticker} on {quarter_end_date}: {graham_number}")

            date = get_reported_date(ticker, quarter_end_date)
            price = get_closing_price(ticker, date)
            print(f"Closing price for {ticker} on {date}: {price}")
            acceptable_price = calculate_acceptable_price(ticker, date)

            # find the undervalued stocks
            if acceptable_price > price:
                difference = acceptable_price / price
                portfolio[ticker] = difference

        except:
            print(f"Skipping {ticker} due to missing graham_number or price.")

    # Sort by Ratio
    sorted_portfolio = sorted(portfolio.items(), key=lambda x: x[1], reverse=True)

    # Take the first 30 companies for the portfolio
    top_30_result = dict(sorted_portfolio)

    return top_30_result

'''def create_portfolio(ticker_list, quarter_end_date):
    portfolio = {}
    for ticker in ticker_list:

        try:
            #graham_number = calculate_graham_number(ticker, quarter_end_date)
            graham_number =  calculate_gn_with_avg_eps(ticker, quarter_end_date)
            print(f"Graham number for {ticker} on {quarter_end_date}: {graham_number}")

            date = get_reported_date(ticker, quarter_end_date)
            price = get_closing_price(ticker, date)
            print(f"Closing price for {ticker} on {date}: {price}")

            # find the undervalued stocks
            if graham_number is not None and price is not None:
                margin_of_safety = graham_number - price

                if margin_of_safety > 0:
                    portfolio[ticker] = margin_of_safety

        except:
            print(f"Skipping {ticker} due to missing graham_number or price.")

    # Sort by Ratio
    sorted_portfolio = sorted(portfolio.items(), key=lambda x: x[1], reverse=True)

    # Take the first 30 companies for the portfolio
    top_30_result = dict(sorted_portfolio[:30])

    return top_30_result'''


'''def create_portfolio(ticker_list, quarter, year):
    portfolio = {}

    for ticker in ticker_list:
        graham_number = calculate_graham_number(ticker, quarter, year)
        date = get_reported_date(ticker, quarter, year)
        price = get_closing_price(ticker, date)
        ratio = graham_number / price

        portfolio[ticker] = ratio

    sorted_portfolio = dict(sorted(portfolio.items(), key=lambda x: x[1], reverse=True))
    return sorted_portfolio'''


'''def create_portfolio(ticker_list, quarter_end_date):
    portfolio = {}

    for ticker in ticker_list:
        graham_number = calculate_graham_number(ticker, quarter_end_date)
        print(graham_number)
        date = get_reported_date(ticker, quarter_end_date)
        price = get_closing_price(ticker, date)
        print(price)

        # Check if both graham_number and price are not None before calculating ratio
        if graham_number is not None and price is not None:
            ratio = graham_number / price # irgendwas um zu verhindern, dass durch 0 geteilt wird?
            portfolio[ticker] = ratio
            print(ratio)
        else:
            print(f"Skipping {ticker} due to missing graham_number or price.")


    #sorted_portfolio = dict(sorted(portfolio.items(), key=lambda x: x[1], reverse=True))
    #return sorted_portfolio
    return portfolio'''


'''tickers = ['AAPL', 'MSFT', 'PEP']

print(create_portfolio(tickers, 'Q2', '2020'))'''


'''def create_portfolio(ticker_list, quarter_end_date):
    portfolio = {}

    for ticker in ticker_list:

        try:

            graham_number = calculate_graham_number(ticker, quarter_end_date)
            print(f"Graham number for {ticker} on {quarter_end_date}: {graham_number}")

            date = get_reported_date(ticker, quarter_end_date)
            price = get_closing_price(ticker, date)
            print(f"Closing price for {ticker} on {date}: {price}")

            # Check if both graham_number and price are not None before calculating ratio
            if graham_number is not None and price is not None:
                ratio = graham_number / price
                print(f"Ratio for {ticker} on {quarter_end_date}: {ratio}")

                # Add the ticker and its ratio to the portfolio dictionary
                portfolio[ticker] = ratio

        except:
            print(f"Skipping {ticker} due to missing graham_number or price.")

    # Sort by Ratio
    sorted_portfolio = sorted(portfolio.items(), key=lambda x: x[1], reverse=True)

    # Take the first 30 companies for the portfolio
    top_30_result = dict(sorted_portfolio[:30])

    return top_30_result'''


'''ticker = ['AAPL', 'MSFT', 'C', 'AIG']
date = '2003-12-31'
portfolio = create_portfolio(ticker, date)
print(portfolio)'''
