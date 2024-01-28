import os
import argparse
import requests
from requests import HTTPError
from dotenv import load_dotenv

from helper import format_number

load_dotenv()

def main():

    API_KEY_FMP = os.getenv('API_KEY_FMP')
    API_KEY_ALPHA = os.getenv('API_KEY_ALPHA')

    parser = argparse.ArgumentParser(description='Analyze TICKER')
    parser.add_argument('ticker', help='Ticker you wish to look up', type=str) # args.ticker

    args = parser.parse_args()

    try:

        # FMP API
        balance_sheet_API = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{args.ticker}?period=annual&apikey={API_KEY_FMP}')
        key_metrics_API = requests.get(f'https://financialmodelingprep.com/api/v3/key-metrics/{args.ticker}?period=annual&apikey={API_KEY_FMP}')
        quote_API = requests.get(f'https://financialmodelingprep.com/api/v3/quote/{args.ticker}?apikey={API_KEY_FMP}')
        dividends_API = requests.get(f'https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{args.ticker}?apikey={API_KEY_FMP}')

        # Alpha Advantage API
        earnings_API = requests.get(f'https://www.alphavantage.co/query?function=EARNINGS&symbol={args.ticker}&apikey={API_KEY_ALPHA}')
        balance_sheet_ALPHA_API = requests.get(f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={args.ticker}&apikey={API_KEY_ALPHA}')
        
        balance_sheet_API.raise_for_status()
        key_metrics_API.raise_for_status()
        quote_API.raise_for_status()
        dividends_API.raise_for_status()

        earnings_API.raise_for_status()
        balance_sheet_ALPHA_API.raise_for_status()

        balance_sheet = balance_sheet_API.json()
        key_metrics = key_metrics_API.json()
        quote = quote_API.json()
        dividends_data = dividends_API.json()

        earnings_API_data = earnings_API.json()
        balance_sheet_ALPHA_data = balance_sheet_ALPHA_API.json()

        # Quote data
        market_cap = float(quote[0]['marketCap'])
        price_percentage_change = float(quote[0]['changesPercentage'])
        pe_ratio = float(quote[0]['pe'])
        stock_price = float(quote[0]['price'])

        # Balance Sheet FMP data
        cash_and_short_term_investments = float(balance_sheet[0]['cashAndShortTermInvestments'])
        net_receivables = float(balance_sheet[0]['netReceivables'])
        inventory = float(balance_sheet[0]['inventory'])
        total_liabilities = float(balance_sheet[0]['totalLiabilities'])
        shares_outstanding = float(quote[0]['sharesOutstanding'])
        current_assets = float(balance_sheet[0]['totalCurrentAssets'])
        current_liabilities = float(balance_sheet[0]['totalCurrentLiabilities'])
        total_assets = float(balance_sheet[0]['totalAssets'])
        intangible_assets = float(balance_sheet[0]['intangibleAssets']) # or goodwillAndIntangibleAssets
        total_debt = float(balance_sheet[0]['totalDebt'])
        longterm_debt = float(balance_sheet[0]['longTermDebt']) # As per Graham should also include Preferred stock - Deferred Tax Liabilities (not sure it is included)
        stockholders_equity = float(balance_sheet[0]['totalStockholdersEquity'])
        preferred_stock = float(balance_sheet[0]['preferredStock'])

        # Balance Sheet Alpha data
        all_shares_outstanding = [format_number(float(item['commonStockSharesOutstanding'])) for item in balance_sheet_ALPHA_data['annualReports']]

        # Ratios
        working_capital = current_assets - current_liabilities

        # Key Metrics
        net_income_per_share = [float(item['netIncomePerShare']) for item in key_metrics] # Last 5 years

        #* 1. Calculate NNWC
        NNWC = (cash_and_short_term_investments + (0.75 * net_receivables) + (0.5 * inventory) - total_liabilities) / shares_outstanding
        NNWC_risk_factor = NNWC * 0.66666
        print(f'Current Price: {stock_price}')
        print(f'NNWC Risk Factor: {NNWC_risk_factor:.2f}')
        print('===============================')

        #* 2. Market Cap
        print(f'Market Cap: {format_number(market_cap)}')
        print('===============================')

        #* 3. Financial Condition
        current_ratio = current_assets / current_liabilities

        print(f'Current ratio > 2: {current_ratio > 2}; Current Ratio: {current_ratio:.2f}')
        print(f'Long-term Debt < Working Capital: {longterm_debt < working_capital}')
        print('===============================')

        #* 4. Earnings Stability
        EPS_last_10_years = [float(data['reportedEPS']) for data in earnings_API_data['annualEarnings'][:10]]
        
        print(f'Negative EPS last 10 years: {any(eps < 0 for eps in EPS_last_10_years)}')
        print(f'EPS last 10 years: {EPS_last_10_years}')
        print('EPS[0] = Current year')
        print('===============================')
        
        #* 5. Dividend Record (uninterrupted payments for at least the past 20 years)
        dividends_historical = [row['dividend'] for row in dividends_data['historical'][:20]]
        dividends_historical_dates = [row['date'] for row in dividends_data['historical']]
        
        if bool(dividends_historical) is False:
            print(f'No dividends record.')
            print('===============================')
        else:
            print(f'Negative Dividends last 20 years: {any(dividend < 0 for dividend in dividends_historical)}')
            print(f'Dividends last 20 years: {dividends_historical}')
            print(f'Dividens since: {dividends_historical_dates[-1]}')
            print('List[0] = Current year')
            print('===============================')

        #* 6. EPS Average Growth
        if len(EPS_last_10_years) == 10:
            y0, y1, y2 =  EPS_last_10_years[:3]
            y8, y9, y10 = EPS_last_10_years[7:10]

            EPS_average_current_3_years = (y0 + y1 + y2) / 3
            EPS_average_last_3_years = (y8 + y9 + y10) / 3

            EPS_growth_average = ((EPS_average_current_3_years - EPS_average_last_3_years) / EPS_average_last_3_years)

            print(f'Average EPS current 1-3: {EPS_average_current_3_years:.2f}')
            print(f'Average EPS 7-10: {EPS_average_last_3_years:.2f}')
            print(f'EPS Growth: {EPS_growth_average:.2f}')
            print('===============================')

        else:
            y0, y1, y2 =  EPS_last_10_years[:3]

            EPS_average_current_3_years = (y0 + y1 + y2) / 3

            print(f'Limited amount of EPS data.')
            print(f'Average EPS last 3 years: {EPS_average_current_3_years:.2f}')
            print('===============================')


        #* 7. P/E Ratio
        pe_ratio_averaged_last_3_years = stock_price / EPS_average_current_3_years

        print(f'P/E (Price / average EPS last 3 years): {pe_ratio_averaged_last_3_years:.2f}')
        print(f'P/E < 15: {pe_ratio_averaged_last_3_years < 15}')
        print('===============================')

        #* 8. P/B Ratio
        book_value_per_share = (stockholders_equity - preferred_stock) / shares_outstanding
        pb_ratio = stock_price / book_value_per_share

        print(f'Book Value per Share: {book_value_per_share:.2f}')
        print(f'P/B Ratio: {pb_ratio:.2f}')
        print(f'P/B Ratio < 1.5: {pb_ratio < 1.5}')
        print('===============================')

        #* 9. PB * PE < 22.5
        pb_pe_multiple = pe_ratio * pb_ratio
        print(f'P/B * P/E: {pb_pe_multiple:.2f}')
        print(f'P/B * P/E < 22.5: {(pb_ratio * pe_ratio) < 22.5}')
        print('===============================')

        #* 10. Shares Outstanding Changes
        print(f'Shares Outstanding Last 5 years: {all_shares_outstanding}')
        print('===============================')

        #* 11. Debt to Equity
        debt_to_equity = total_liabilities / stockholders_equity
        print(f'Debt to Equity < 2: {debt_to_equity < 2}, Debt to Equity: {debt_to_equity:.2f}')
        print('===============================')

    
    except HTTPError as e:
        print(e)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()