from credentials import api_key
import zipfile
from datetime import datetime
from util import get_quarters_df
from main import create_portfolio
from util import get_quarters_df
from util import get_ticker_list_for_target_date
import math
import os
import pandas as pd

# functions

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


'''def calculate_gn_with_avg_eps(ticker, target_date):
    graham_num_data = {"Ticker":ticker}
    # Get key metrics
    key_metrics = get_key_metrics('../key-metrics.zip', ticker)

    # Define the time window based on the quarter of the target date
    target_date = pd.to_datetime(target_date)
    print(target_date)
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
            print(avg_eps)
            graham_num_data['EPS'] = avg_eps

            bvps = row['bookValuePerShare']
            print(bvps)
            graham_num_data['BVPS'] = bvps

            # Check if avg_eps and bvps are non-negative before calculating Graham number
            if avg_eps >= 0 and bvps >= 0:
                graham_number = math.sqrt(22.5 * avg_eps * bvps)
                print(graham_number)

            else:
                graham_number = None

            graham_num_data['GrahamNumber'] = graham_number

    # price:
    date = target_date.strftime('%Y-%m-%d')
    price = get_closing_price(ticker, date)
    graham_num_data['ClosingPrice'] = price

    return graham_num_data


quarters = get_quarters_df()


for index, row in quarters.iterrows():
    # Initialize an empty list to store the dictionaries for each quarter
    quarter_data = []

    quarter = row['end_date'].strftime("%Y-%m-%d")
    print(quarter)

    ticker_list = get_ticker_list_for_target_date(quarter)
    print(ticker_list)

    # Loop through each quarter and ticker to collect the metrics
    for ticker in ticker_list:
        try:
            print(ticker)
            ticker_data = calculate_gn_with_avg_eps(ticker, quarter)

            #metrics_dict = get_metrics(ticker, quarter)
            quarter_data.append(ticker_data)

            # Create a DataFrame from the list of dictionaries
            df = pd.DataFrame(quarter_data)

            # Save the DataFrame to a CSV file for each quarter
            csv_file_name = f'quarterly_metrics_{quarter}.csv'
            df.to_csv(csv_file_name, index=False)
            print(f"Saved {csv_file_name}")
        except Exception as e:
            print(e)
'''


def calculate_ratios(input_file, output_folder):
    # Lade die CSV-Datei
    data = pd.read_csv(input_file)

    # Extrahiere das Datum aus dem Dateinamen
    date_str = os.path.basename(input_file).split('_')[2].split('.')[0]

    # Füge die Spalten KGV und KBV hinzu
    if 'EPS' in data.columns and 'ClosingPrice' in data.columns:
        data['KGV'] = data.apply(lambda row: row['ClosingPrice'] / row['EPS'] if pd.notna(row['EPS']) and row['EPS'] != 0 else None, axis=1)
    else:
        print('Warnung: "EPS" oder "ClosingPrice" nicht in den Spalten vorhanden, KGV wird nicht berechnet.')

    if 'BVPS' in data.columns and 'ClosingPrice' in data.columns:
        data['KBV'] = data.apply(lambda row: row['ClosingPrice'] / row['BVPS'] if pd.notna(row['BVPS']) and row['BVPS'] != 0 else None, axis=1)
    else:
        print('Warnung: "BVPS" oder "ClosingPrice" nicht in den Spalten vorhanden, KBV wird nicht berechnet.')

    # Erstelle den Ausgabepfad
    output_file = os.path.join(output_folder, f'metrics_with_ratios_{date_str}.csv')

    # Speichere die aktualisierten Daten in einer neuen CSV-Datei
    data.to_csv(output_file, index=False)

    print(f'Die Daten wurden aktualisiert und in {output_file} gespeichert.')

# Passe diese Pfade entsprechend deiner Ordnerstruktur an
input_folder = '.'  # Annahme: Dateien befinden sich im gleichen Ordner wie das Skript
output_folder = 'ratios_metrics'

# Überprüfe, ob der Ausgabeordner existiert, wenn nicht, erstelle ihn
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Durchlaufe alle CSV-Dateien im Eingabeordner und aktualisiere sie
for file_name in os.listdir(input_folder):
    if file_name.startswith('quarterly_metrics') and file_name.endswith('.csv'):
        input_path = os.path.join(input_folder, file_name)
        calculate_ratios(input_path, output_folder)
