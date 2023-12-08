import time
import requests
import os
import pandas as pd


API_KEY = "MGHTO3SRB14CE5VU"

daily_commodities = ["WTI", "BRENT", "NATURAL_GAS"]
monthly_commodities = ["COPPER", "ALUMINUM", "WHEAT", "CORN", "COTTON", "SUGAR", "COFFEE", "ALL_COMMODITIES"]
POSTFIX = "_AlphaVantage"
FOLDER = "datasets/"

for commodity in daily_commodities + monthly_commodities:
    response = requests.get(f"https://www.alphavantage.co/query?apikey={API_KEY}&function={commodity}&interval=daily").json()
    if "Note" in response:
        print("Reached Per Minute API limit, waiting 1 minute to continue")
        time.sleep(65)
        response = requests.get(f"https://www.alphavantage.co/query?apikey={API_KEY}&function={commodity}&interval=daily").json()
        if "Note" in response:
            print("Reached Daily API limit, try again tomorrow")
            quit()

    df = pd.DataFrame(response["data"])
    df.rename(columns={"date": "Date", "value": "Close"}, inplace=True)
    df.drop(df.loc[df['Close'] == "."].index, inplace=True)

    file_location = FOLDER + commodity + POSTFIX + ".xlsx"
    if os.path.exists(file_location):
        os.remove(file_location)

    df.to_excel(file_location, index=False)
    print(f"Successfully downloaded data for {commodity}")
