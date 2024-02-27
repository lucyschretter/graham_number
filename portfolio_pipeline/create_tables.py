from credentials import api_key
import zipfile
from datetime import datetime
from util import get_closing_price
from util import get_key_metrics
from util import get_quarters_df
from main import create_portfolio
from util import get_quarters_df
from util import get_ticker_list_for_target_date
import math
import os
import pandas as pd


def calculate_gn_with_avg_eps(ticker, target_date):
    """
    function to calculate graham number like in util.py but append interim results to dataframe
    :param ticker: ticker symbol of the required company
    :param target_date: quarter date
    :return: DataFrame with columns CosingPrice, Graham Number , average EPS and BVPS
    """
    graham_num_data = {"Ticker": ticker}
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


'''
quarters = get_quarters_df()
for index, row in quarters.iterrows():
    # Initialize an empty list to store the dictionaries for each quarter
    quarter_data = []

    quarter = row['date'].strftime("%Y-%m-%d")
    print(quarter)

    ticker_list = get_ticker_list_for_target_date(quarter)
    print(ticker_list)

    # Loop through each quarter and ticker to collect the metrics
    for ticker in ticker_list:
        try:
            print(ticker)
            ticker_data = calculate_gn_with_avg_eps(ticker, quarter)
            
            quarter_data.append(ticker_data)

            # Create a DataFrame from the list of dictionaries
            df = pd.DataFrame(quarter_data)

            # Save the DataFrame to a CSV file for each quarter
            csv_file_name = f'key_metrics_with_average_eps/quarterly_metrics_{quarter}_avg_eps.csv'
            df.to_csv(csv_file_name, index=False)
            print(f"Saved {csv_file_name}")
        except Exception as e:
            print(e)'''


# calculate price earnings ratio and price book value ratio from quarterly metrics (see above)

def calculate_ratios(input_file, output_folder):
    """
    calculate price earnings ratio and price book value ratio from quarterly metrics
    :param input_file: DataFrame with columns EPS, BVPS, GrahamNumber, ClosingPrice
    :param output_folder: path where the result dataframe will be saved to
    :return: DataFrame with columns EPS, BVPS, GrahamNumber, ClosingPrice, KGV (= price earnings ratio), KBV (=price book value ratio)
    """
    # load csv
    data = pd.read_csv(input_file)

    # Extract the date from the file name
    date_str = os.path.basename(input_file).split('_')[2].split('.')[0]

    # Add the columns KGV (P/E ratio) and KBV (P/B ratio)
    if 'EPS' in data.columns and 'ClosingPrice' in data.columns:
        data['KGV'] = data.apply(
            lambda row: row['ClosingPrice'] / row['EPS'] if pd.notna(row['EPS']) and row['EPS'] != 0 else None, axis=1)
    else:
        print('Warnung: "EPS" oder "ClosingPrice" nicht in den Spalten vorhanden, KGV wird nicht berechnet.')

    if 'BVPS' in data.columns and 'ClosingPrice' in data.columns:
        data['KBV'] = data.apply(
            lambda row: row['ClosingPrice'] / row['BVPS'] if pd.notna(row['BVPS']) and row['BVPS'] != 0 else None,
            axis=1)
    else:
        print('Warnung: "BVPS" oder "ClosingPrice" nicht in den Spalten vorhanden, KBV wird nicht berechnet.')

    # Create the output path
    output_file = os.path.join(output_folder, f'metrics_with_ratios_{date_str}.csv')

    # Save the updated data to a new CSV file
    data.to_csv(output_file, index=False)

    print(f'Die Daten wurden aktualisiert und in {output_file} gespeichert.')


# Adjust these paths according to your folder structure
input_folder = 'key_metrics_per_quarter_with_avg_eps'  # Annahme: Dateien befinden sich im gleichen Ordner wie das Skript
output_folder = 'key_metrics_per_quarter_with_avg_eps_with_ratios'

# Check if the output folder exists, if not, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Iterate through all CSV files in the input folder and update them
for file_name in os.listdir(input_folder):
    if file_name.startswith('quarterly_metrics') and file_name.endswith('.csv'):
        input_path = os.path.join(input_folder, file_name)
        calculate_ratios(input_path, output_folder)
