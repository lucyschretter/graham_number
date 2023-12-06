from main import create_portfolio
from util import get_quarters_df
from util import get_ticker_list_for_target_date

quarters_df = get_quarters_df()


if __name__ == "__main__":

    for index, row in quarters_df.iterrows():
        date = row['date'].strftime("%Y-%m-%d")
        print(date)
        quarter = row['quarter']
        print(quarter)
        year = row['year']
        print(year)

        ticker_list = get_ticker_list_for_target_date(date)
        print(ticker_list)

        try:
            result = create_portfolio(ticker_list, quarter, year)
            print(result)
        except:
            print('no undervalued companies')