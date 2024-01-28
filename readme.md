## Stock analysis

Python script that analyzes stocks based on Graham's criteria (plus some small additional criterias). 

Fetches data from two public APIs (API key is required for both). 

## Usage
`python analyze.py TICKER`

Output is very simple, prints results into the console (just for quick analysis).

I am also using more advanced version with **cronjob** that regularly checks stocks and sends me an email with better output using **python logging module**.

I am still tweaking it as I learn more about technical analysis. Changing/adding criterias.