# imports
import pandas as pd
import math
import zipfile
from credentials import api_key
# import yfinance as yf
from datetime import datetime


def get_quarters_df(start_date="1999-12-31", end_date="2022-12-31"):
    # quarterly: freq='Q'
    quarters = pd.date_range(start=start_date, end=end_date, freq='Q')
    quarters_df = pd.DataFrame({'date': quarters})
    # Extract quarter and year information
    quarters_df['quarter'] = quarters_df['date'].dt.to_period("Q")
    quarters_df['year'] = quarters_df['date'].dt.year
    quarters_df['quarter'] = 'Q' + quarters_df['quarter'].astype(str).str.split('Q').str[1]

    return quarters_df


def get_ticker_list_for_target_date(target_date: str):
    df = pd.read_csv('S&P 500 Historical Components & Changes(08-01-2023).csv', index_col='date')
    df.index = pd.to_datetime(df.index)
    df['tickers'] = df['tickers'].apply(lambda x: sorted(x.split(',')))
    df = df.resample('Q').first()

    # Loop through the ticker DataFrame and get historical data for each quarter
    for index, row in df.iterrows():
        tickers = row['tickers']
        date_str = index.strftime("%Y-%m-%d")

        if date_str == target_date:
            return tickers


def get_key_metrics(zip_file_path: str, ticker: str):
    """
    :param zip_file_path: file path of the zip folder the key_metrics.json file is stored in
    :param ticker: ticker symbol as string
    :return: pandas dataframe containing key metrics for the given ticker symbol
    """
    file_name = f'{ticker}_key-metrics.json'
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        with zip_ref.open(file_name) as file:
            content = pd.read_json(file)
            return content


def get_nearest_date(items, pivot):
    """
    Finds the nearest date in a list of date strings to a given pivot date.
    (source: https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date)
    :param items: (list of str) A list containing date strings in the format "%Y-%m-%d".
    :param pivot: (str) The date string in the format "%Y-%m-%d" to which the nearest date is sought.
    :return: nearest (datetime): The nearest datetime object to the pivot date.
            timedelta (timedelta): The time difference between the nearest date and the pivot date.
    """
    # Convert the date strings to datetime objects
    items = [datetime.strptime(date, "%Y-%m-%d") for date in items]
    pivot = datetime.strptime(pivot, "%Y-%m-%d")

    nearest = min(items, key=lambda x: abs(x - pivot))
    timedelta = abs(nearest - pivot)
    return nearest, timedelta


def get_closing_price(ticker: str, target_date: str):
    """
    Get the closing price of a ticker on a given target date.
    If there is no possible way through an API, the function returns the nearest closing price.
    :param ticker: ticker symbol as string
    :param target_date: target date as string
    :return: (nearest) closing price as float
    """

    closing_price = None

    alpha_vantage_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={api_key}&datatype=csv'
    alpha_vantage_csv = pd.read_csv(alpha_vantage_url)
    alpha_vantage_df = pd.DataFrame(alpha_vantage_csv)

    # Try fetching from Alpha Vantage
    for index, row in alpha_vantage_df.iterrows():
        if row['timestamp'] == target_date:
            closing_price = row['close']
            # print(f"Found exact match in Alpha Vantage: {closing_price}")
            return closing_price

    '''if closing_price is None:
        # If Alpha Vantage fails, try fetching from Yahoo Finance
        yfinance_ticker = yf.Ticker(ticker)
        historical_data = yfinance_ticker.history(period="25y")

        for index, row in historical_data.iterrows():
            date = index.strftime("%Y-%m-%d")
            if date == target_date:
                closing_price = row['Close']
                # print(f"Found exact match in Yahoo Finance: {closing_price}")
                return closing_price'''

    if closing_price is None:
        # If both fail, find the nearest closing price
        dates = alpha_vantage_df['timestamp']
        nearest_date, timedelta = get_nearest_date(dates, target_date)

        # Get closing price of nearest date
        nearest_date_str = nearest_date.strftime("%Y-%m-%d")
        for index, row in alpha_vantage_df.iterrows():
            if row['timestamp'] == nearest_date_str:
                nearest_closing_price = row['close']
                # print(f"Found nearest closing price: {nearest_closing_price} on {nearest_date_str}")
                return nearest_closing_price
    else:
        return closing_price


# function to get the reported day for a specific quarter of a company

def get_reported_date(ticker: str, target_quarter: str, target_year: str):
    """
    Some companies report their metrics on different dates.
    This function returns the reported date for the target quarter (and year).
    :param ticker: ticker symbol as string
    :param target_quarter: target quarter as string
    :param target_year: target year as string
    :return: The reported date in the format "%Y-%m-%d" that will be used as the target date later.
    """
    # Get key metrics
    key_metrics = get_key_metrics('key-metrics_3-Aktien.zip', ticker)
    for index, row in key_metrics.iterrows():
        quarter = row['period']
        year = str(row['calendarYear'])

        if quarter == target_quarter and year == target_year:
            target_date = row['date'].strftime("%Y-%m-%d")
            return target_date


def calculate_graham_number(ticker: str, target_quarter: str, target_year: str):
    """
    This function calculates the Graham Number of a ticker from the EPS and BVPS.
    If any of the values is negative, the function takes the column (grahamNumber) to avoid math error.
    :param ticker: ticker symbol
    :param target_quarter: target quarter
    :param target_year: target year
    :return: graham number of a ticker as float (= intrinsic value)
    """
    # Get key metrics
    key_metrics = get_key_metrics('key-metrics_3-Aktien.zip', ticker)
    for index, row in key_metrics.iterrows():
        quarter = row['period']
        year = str(row['calendarYear'])

        if quarter == target_quarter and year == target_year:
            eps = row['netIncomePerShare']
            bvps = row['bookValuePerShare']

            # Check if eps and bvps are non-negative before calculating Graham number
            if eps >= 0 and bvps >= 0:
                graham_number = math.sqrt(22.5 * eps * bvps)
                # print(f'The calculated Graham number on {target_date} is {graham_number}')

            else:
                graham_number = row['grahamNumber']
                # print("EPS or BVPS is negative. Took the given Graham Number instead of calculating it.")

            return graham_number


def get_margin_of_safety(ticker: str, target_quarter: str, target_year: str):
    """
    This function returns the margin of safety which will be used to create the portfolio
    :param ticker: ticker symbol
    :param target_quarter: target quarter
    :param target_year: target year
    :return: margin of safety as float
    """

    target_date = get_reported_date(ticker, target_quarter, target_year)
    closing_price = get_closing_price(ticker, target_date)
    graham_number = calculate_graham_number(ticker, target_quarter, target_year)

    # find the undervalued stocks
    if graham_number is not None and closing_price is not None:
        margin_of_safety = graham_number - closing_price
        return margin_of_safety
    else:
        return 'some values are missing'
