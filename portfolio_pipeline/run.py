from main import create_portfolio
from util import get_quarters_df
from util import get_ticker_list_for_target_date

import json


quarters = get_quarters_df()


# save data
result_dict = {}

if __name__ == "__main__":
    for index, row in quarters.iterrows():
        # date = row['end_date'].strftime("%Y-%m-%d")
        date = row['date'].strftime("%Y-%m-%d")
        print(date)

        ticker_list = get_ticker_list_for_target_date(date)
        print(ticker_list)

        result = create_portfolio(ticker_list, date)
        if result is not None:
            result_dict[date] = result


print(result_dict)

# Save the dictionary as a JSON file
with open('portfolios_new', 'w') as json_file:
    json.dump(result_dict, json_file)
