"""
get via csv file from github
source code: https://github.com/fja05680/sp500/blob/master/sp500_by_date.ipynb

dates range from 1996-01-02 to 2023-06-20
source csv: https://github.com/fja05680/sp500/blob/master/S%26P%20500%20Historical%20Components%20%26%20Changes(08-01-2023).csv
"""

import pandas as pd
from collections import Counter


def get_quarterly_df(filename: str):
    df = pd.read_csv(filename, index_col='date')
    df.index = pd.to_datetime(df.index)
    df['tickers'] = df['tickers'].apply(lambda x: sorted(x.split(',')))
    quarterly_df = df.resample('Q').first()

    return quarterly_df


def get_ticker_list_for_target_date(target_date: str):
    """
    :param target_date: target_date has to be the last day of a quarter
    :return: list
    """

    df = get_quarterly_df('S&P 500 Historical Components & Changes(08-01-2023).csv')

    # Loop through the quarterly DataFrame and get historical data for each quarter
    for index, row in df.iterrows():
        tickers = row['tickers']
        date_str = index.strftime("%Y-%m-%d")

        if date_str == target_date:
            return tickers


def get_most_common_tickers():
    df = get_quarterly_df('S&P 500 Historical Components & Changes(08-01-2023).csv')

    # Initialize the list with companies from the first row
    common_tickers = list(df.iloc[0]['tickers'])

    # Loop through the quarterly DataFrame and get historical data for each quarter
    for index, row in df.iterrows():
        tickers = row['tickers']

        # Update the list with the intersection of current tickers and previous tickers
        common_tickers = list(set(common_tickers) & set(tickers))

    return sorted(common_tickers)


def get_unique_companies():
    df = get_quarterly_df('S&P 500 Historical Components & Changes(08-01-2023).csv')

    # Create an empty set to store unique tickers
    unique_tickers = set()

    # Loop through the DataFrame and add all unique tickers to the set
    for tickers_list in df['tickers']:
        unique_tickers.update(tickers_list)

    # Convert the set to a list for printing or further use
    unique_tickers_list = list(unique_tickers)

    # Print the list of unique tickers
    return sorted(unique_tickers_list)


def get_ticker_frequency():
    df = get_quarterly_df('S&P 500 Historical Components & Changes(08-01-2023).csv')

    # Create a Counter to store the frequency of each company
    ticker_frequency = Counter()

    # Loop through the quarterly DataFrame and get historical data for each quarter
    for _, row in df.iterrows():
        tickers = set(row['tickers'])

        # Update the Counter with the companies present in each quarter
        ticker_frequency.update(tickers)

    sorted_ticker_frequency = ticker_frequency.most_common()

    return sorted_ticker_frequency


# result = get_ticker_frequency()
# for ticker, count in result:
    # print(f"{ticker}: {count} times in index")

# print(len(get_unique_companies()))
