from datetime import datetime, timedelta
import json
from credentials import api_key
import pandas as pd


# define functions to scrape prices
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
    items = [datetime.strptime(date, "%Y-%m-%d") for date in items]
    pivot = datetime.strptime(pivot, "%Y-%m-%d")

    if not items:
        return None, None

    nearest = min(items, key=lambda x: abs(x - pivot))
    timedelta = abs(nearest - pivot)
    return nearest, timedelta

def get_adjusted_closing_price(ticker: str, target_date: str):
    """
    Get the adjusted closing price of a ticker on a given target date.
    If there is no possible way through an API, the function returns the nearest closing price.
    :param ticker: ticker symbol as string
    :param target_date: target date as string
    :return: (nearest) adjusted closing price as float
    """
    closing_price = None

    try:
        alpha_vantage_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={api_key}&datatype=csv'
        alpha_vantage_csv = pd.read_csv(alpha_vantage_url)
        alpha_vantage_df = pd.DataFrame(alpha_vantage_csv)

        for index, row in alpha_vantage_df.iterrows():
            if row['timestamp'] == target_date:
                closing_price = row['adjusted_close']
                return closing_price

        if closing_price is None:
            dates = alpha_vantage_df['timestamp']
            nearest_date, timedelta = get_nearest_date(dates, target_date)

            nearest_date_str = nearest_date.strftime("%Y-%m-%d")
            for index, row in alpha_vantage_df.iterrows():
                if row['timestamp'] == nearest_date_str:
                    nearest_closing_price = row['adjusted_close']
                    return nearest_closing_price
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Funktion zur Berechnung der Renditen des Portfolios
def calculate_return(start_date, portfolios):
    """
    Calculate the total return of a portfolio from a specified start date (investment date)
    :param start_date: The start date of the investment in the format "%Y-%m-%d"
    :param portfolios: A dictionary containing portfolios with ticker lists for different start dates
    :return: The total return of the portfolio

    """
    try:
        # get ticker_list from dictionary:
        ticker_list = portfolios[start_date]
        print(ticker_list)

        start_values = {ticker: get_adjusted_closing_price(ticker, start_date) for ticker in ticker_list}
        print(start_values)
        total_start_values = sum(start_values.values())
        print(total_start_values)

        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6 * 365)).strftime("%Y-%m-%d")
        end_values = {ticker: get_adjusted_closing_price(ticker, end_date) for ticker in ticker_list}
        print(end_values)
        total_end_values = sum(end_values.values())
        print(total_end_values)


        # Berechnung der Gesamtrendite des Portfolios
        total_return = ((total_end_values - total_start_values) / total_start_values)

        print(f"investment_start: {start_date}, investment_end: {end_date}, total_return: {total_return}")
        return total_return
    except:
        return f"there is not enough data for start quarter {start_date}"


# Load JSON content from files
with open('..\\portfolio_pipeline\\portfolios_final.json', 'r') as file1:
    portfolios_dict = json.load(file1)

# restructure portfolio dictionary
portfolios_dict_cleaned = {}
for key, value in portfolios_dict.items():
    portfolios_dict_cleaned[key] = [k for k in value.keys()]


# define (investment) start dates
start_dates = list(portfolios_dict.keys())

# variable to save results to
results = {}

for i, start_date in enumerate(start_dates):
    try:
        print('Start date: ', start_date)
        ticker_list = portfolios_dict_cleaned[start_date]
        print(ticker_list)

        start_values = {ticker: get_adjusted_closing_price(ticker, start_date) for ticker in ticker_list}
        total_start_values = sum(start_values.values())

        result_list = []

        # iterate through 24 quarters (=6 years)
        for y in range(1, 25):
            if i + y < len(start_dates):
                print(i + y)
                end_date = start_dates[i + y]
                print(end_date)

                end_values = {ticker: get_adjusted_closing_price(ticker, end_date) for ticker in ticker_list}
                total_end_values = sum(end_values.values())

                total_return_for_period = ((total_end_values - total_start_values) / total_start_values)

                print(f"Investment start: {start_date}, Investment end: {end_date}, Total return: {total_return_for_period}")

                # add period-return pair to result list
                result_list.append({f'Period-{y}': total_return_for_period})

                # update total_start_values for next iteration
                total_start_values = total_end_values
            else:
                print('Daten außerhalb des Untersuchungszeitraums')

        # add list with period-return pair to result dictionary
        results[start_date] = result_list

        # write results for start_date to json file
        with open(f'final_results_data/final_results_{start_date}.json', 'w') as outfile:
            json.dump(results, outfile)

        # clean results dict
        results = {}

    except Exception as e:
        print(f"Fehler für {start_date}: {e}")

'''

# merge jsons (in this case first two quarters...)

with open('final_results_data/final_results_2000-03-31.json', 'r') as file1:
    data1 = json.load(file1)
with open('final_results_data/final_results_2000-06-30.json', 'r') as file2:
    data2 = json.load(file2)

# merge data
merged_data = {**data1, **data2}

print(merged_data)

# save combined data to json (and repeat...)
with open('final_results_data/final_returns.json', 'w') as outfile:
    json.dump(merged_data, outfile, indent=2)

'''