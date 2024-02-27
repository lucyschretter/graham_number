from util import get_closing_price
from util import get_reported_date
from util import calculate_acceptable_price


# get ranked portfolio from graham number

def create_portfolio(ticker_list, quarter_end_date):
    """
    :param ticker_list: List of stock tickers to analyze.
    :param quarter_end_date: Quarter-end date for the quarter
    :return: A dictionary containing the top 30 undervalued stocks based on Graham's number, ranked by the acceptable price-to-value ratio.
    """
    portfolio = {}
    for ticker in ticker_list:
        try:
            # Get reported date and closing price
            date = get_reported_date(ticker, quarter_end_date)
            price = get_closing_price(ticker, date)
            print(f"Closing price for {ticker} on {date}: {price}")

            # Calculate acceptable price using the number
            acceptable_price = calculate_acceptable_price(ticker, date)

            # find the undervalued stocks
            if acceptable_price > price:
                difference = acceptable_price / price
                portfolio[ticker] = difference

        except:
            print(f"Skipping {ticker} due to missing graham_number or price.")

    # Sort by Ratio
    sorted_portfolio = sorted(portfolio.items(), key=lambda x: x[1], reverse=True)

    return sorted_portfolio