
import requests
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table', {'id': 'constituents'})

tickers = []

for row in table.find_all('tr')[1:]:
    cells = row.find_all('td')

    symbol = cells[0].text.strip()
    tickers.append(symbol)

for ticker in tickers:
    print(ticker)
