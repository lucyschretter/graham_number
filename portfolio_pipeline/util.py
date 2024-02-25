import pandas as pd
import math
import zipfile
from credentials import api_key
from datetime import datetime


def get_quarters_df(start_date="1999-12-31", end_date="2022-12-31"):
    """
    :param start_date: quarter dataframe starts per default on the last day of 1999
    :param end_date: quarter dataframe end per default on the last day of 2022 (because there was an inconsistency for the s&p lists in 2023)
    :return: dataframe that contains the  quarter data (date, year, quarter)
    """
    # quarterly: freq='Q'
    quarters = pd.date_range(start=start_date, end=end_date, freq='Q')
    quarters_df = pd.DataFrame({'date': quarters})
    # Extract quarter and year information
    quarters_df['quarter'] = quarters_df['date'].dt.to_period("Q")
    quarters_df['year'] = quarters_df['date'].dt.year
    quarters_df['quarter'] = 'Q' + quarters_df['quarter'].astype(str).str.split('Q').str[1]

    return quarters_df

def get_ticker_list_for_target_date(target_date: str):
    """
    function to get the tickers that were in the s&p index on a specific date
    :param target_date: (historical) date on which the portfolio construction will be done
    :return: list of tickers
    """
    df = pd.read_csv('S&P 500 Historical Components & Changes(12-30-2023).csv', index_col='date')
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
    Retrieves key metrics for the given ticker symbol from a JSON file within a zip folder.

    :param zip_file_path: File path of the zip folder containing the key_metrics.json file.
    :param ticker: Ticker symbol as a string.
    :return: Pandas DataFrame containing key metrics for the given ticker symbol.
    """
    file_name = f'{ticker}_key-metrics.json'

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            with zip_ref.open(file_name) as file:
                content = pd.read_json(file)
                return content
    except FileNotFoundError:
        print(f"File {file_name} not found in the provided zip folder path: {zip_file_path}")
        return pd.DataFrame()  # Returning an empty DataFrame on file not found
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def get_nearest_date(items, pivot):
    """
    Finds the nearest date in a list of date strings to a given pivot date.
    (source: https://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date)
    :param items: (list of str) A list containing date strings in the format "%Y-%m-%d".
    :param pivot: (str) The date string in the format "%Y-%m-%d" to which the nearest date is sought.
    :return: nearest (datetime): The nearest datetime object to the pivot date.
            timedelta (timedelta): The time difference between the nearest date and the pivot date.
    """
    if pivot is None:
        return None, None

    # Convert the date strings to datetime objects
    items = [datetime.strptime(date, "%Y-%m-%d") for date in items if type(date) == str]

    if type(pivot) == str:
        pivot = datetime.strptime(pivot, "%Y-%m-%d")


    if not items:
        return None, None

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

    if closing_price is None:
        print(f'Not exact date for {ticker}')
        # find the nearest closing price
        dates = alpha_vantage_df['timestamp']
        nearest_date, timedelta = get_nearest_date(dates, target_date)

        # Check if nearest_date is None
        if nearest_date is None:
            return None

        # Get closing price of nearest date
        nearest_date_str = nearest_date.strftime("%Y-%m-%d")
        for index, row in alpha_vantage_df.iterrows():
            if row['timestamp'] == nearest_date_str:
                nearest_closing_price = row['close']
                # print(f"Found nearest closing price: {nearest_closing_price} on {nearest_date_str}")
                return nearest_closing_price
    else:
        return closing_price


def get_reported_date(ticker: str, target_date: str):
    """
    Some companies report their metrics on different dates.
    This function returns the reported date for the target quarter (and year).
    :param ticker: ticker symbol as string
    :param target_date: target date as string
    :return: The reported date in the format "%Y-%m-%d" that will be used as the target date later.
    """
    # Get key metrics
    key_metrics = get_key_metrics('../key-metrics.zip', ticker)

    # Define the time window based on the quarter of the target date
    target_date = pd.to_datetime(target_date)
    quarter_start_month = (target_date.month - 1) // 3 * 3 + 1
    start_date = pd.to_datetime(f'{target_date.year}-{quarter_start_month:02d}-01')
    end_date = start_date + pd.DateOffset(months=3, days=-1)

    for index, row in key_metrics.iterrows():
        date = pd.to_datetime(row['date']) # convert to datetime to match start and end dates
        # Check if the date is within the desired time window
        if start_date <= date <= end_date:
            date = date.strftime("%Y-%m-%d")
            return date
    else:
        print(f"No data available for this quarter.")
        return None


def calculate_gn_with_avg_eps(ticker, target_date):
    """
    This function calculates the Graham Number of a ticker from the average EPS and BVPS.
    If any of the values is negative, the function will return None
    :param ticker: ticker symbol
    :param target_date: target date
    :return: graham number of a ticker as float (= intrinsic value)
    """
    # Get key metrics
    key_metrics = get_key_metrics('../key-metrics.zip', ticker)

    # Define the time window based on the quarter of the target date
    target_date = pd.to_datetime(target_date)
    quarter_start_month = (target_date.month - 1) // 3 * 3 + 1
    start_date = pd.to_datetime(f'{target_date.year}-{quarter_start_month:02d}-01')
    end_date = start_date + pd.DateOffset(months=3, days=-1)

    for index, row in key_metrics.iterrows():
        date = pd.to_datetime(row['date'])

        # Check if the date is within the desired time window
        if start_date <= date <= end_date:
            # Extract EPS values for the last three years
            eps_values = \
            key_metrics.loc[(key_metrics['date'] >= date - pd.DateOffset(years=3)) & (key_metrics['date'] <= date)][
                'netIncomePerShare']

            # Calculate the average EPS over the last three years
            avg_eps = eps_values.mean()

            bvps = row['bookValuePerShare']

            # Check if avg_eps and bvps are non-negative before calculating Graham number
            if avg_eps >= 0 and bvps >= 0:
                graham_number = math.sqrt(22.5 * avg_eps * bvps)
                print(f'The calculated Graham number on {target_date} is {graham_number}')
                return graham_number

            else:
                graham_number = None

            return graham_number

def get_margin_of_safety(ticker: str, target_date: str):
    """
    This function returns the margin of safety which will be used to create the portfolio
    :param ticker: ticker symbol
    :param target_date: target quarter
    :return: margin of safety as float
    """
    reported_date = get_reported_date(ticker, target_date)
    closing_price = get_closing_price(ticker, reported_date)
    graham_number = calculate_gn_with_avg_eps(ticker, reported_date)

    # find the undervalued stocks
    if graham_number is not None and closing_price is not None:
        margin_of_safety = graham_number / closing_price
        return margin_of_safety
    else:
        print('some values are missing')
        return None

def calculate_acceptable_price(ticker: str, target_date: str):
    """
    This function returns the margin of safety which will be used to create the portfolio
    :param ticker: ticker symbol
    :param target_date: target quarter
    :return: margin of safety as float
    """

    reported_date = get_reported_date(ticker, target_date)
    closing_price = get_closing_price(ticker, reported_date)
    graham_number = calculate_gn_with_avg_eps(ticker, reported_date)

    # find the undervalued stocks
    if graham_number is not None and closing_price is not None:

        acceptable_price = 0.65 * graham_number
        return acceptable_price
    else:
        print('graham number is None')
        return None


def create_portfolio(ticker_list, quarter_end_date):
    portfolio = {}
    for ticker in ticker_list:

        try:
            date = get_reported_date(ticker, quarter_end_date)
            price = get_closing_price(ticker, date)
            print(f"Closing price for {ticker} on {date}: {price}")
            acceptable_price = calculate_acceptable_price(ticker, date)

            # find the undervalued stocks
            if price < acceptable_price:
                difference = acceptable_price / price
                portfolio[ticker] = difference

        except:
            print(f"Skipping {ticker} due to missing graham_number or price.")

    # Sort by Ratio
    sorted_portfolio = sorted(portfolio.items(), key=lambda x: x[1], reverse=True)

    return sorted_portfolio