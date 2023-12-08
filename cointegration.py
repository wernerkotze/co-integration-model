# make the necessary imports
import pandas as pd
import os
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from sklearn.model_selection import train_test_split
import json
from functions import FindCointegratedPairs, GetDatasets, ProduceZScoreTradingSignals, PortfolioPNL
from training_and_testing import CorrelationMatrix, CointegrationPValues, Prices
from training_and_testing import OLSRegression, Spread, Signals, PortfolioPerformance
import matplotlib.pyplot as plt
idx = pd.IndexSlice

# Parse settings
with open("settings.json", "r") as f:
    settings = json.load(f)
    # Define INIT variables
    INIT_CAPITAL = 100000
    TESTING_DATA_ALLOCATION = settings["TestingDataAllocation"]
    if TESTING_DATA_ALLOCATION < 0.2 or TESTING_DATA_ALLOCATION > 0.8:
        err = f"Please setup TrainingDataAllocation in bounds of 0.2 and 0.8 in settings.json"
        raise Exception(err)
    SINGLE_PAIR_MODE = settings["SinglePairMode"]
    PVALUE_THRESHOLD = settings["PValueThreshold"]
    if SINGLE_PAIR_MODE:
        PVALUE_THRESHOLD = 1
        ASSET1 = settings["FirstAsset"]
        ASSET2 = settings["SecondAsset"]
        StdDevMul = settings["StandardDeviationMultiplier"]
        if StdDevMul <= 0:
            err = f"Please check StandardDeviationMultiplier, it can't be less than 0"
            raise Exception(err)
        if ASSET1 == "":
            err = f"Please setup FirstPair in settings.json, you are in SinglePairMode"
            raise Exception(err)
        if not os.path.exists("datasets/"+ASSET1+".xlsx"):
            err = f"Please check FirstPair name, dataset with {ASSET1} doesn't exist"
            raise Exception(err)

        if ASSET2 == "":
            err = f"Please setup SecondPair in settings.json, you are in SinglePairMode"
            raise Exception(err)
        if not os.path.exists("datasets/"+ASSET2+".xlsx"):
            err = f"Please check SecondPair name, dataset with {ASSET2} doesn't exist"
            raise Exception(err)

    else:
        ASSET1 = ""
        ASSET2 = ""
    MODEL_NAME = settings["Name"]
    RESULTS_DIR = "Results" + MODEL_NAME

# Check if results for the name already exits
if os.path.exists(RESULTS_DIR):
    err = f"Results with name {MODEL_NAME} already exist, change name in Settings.json or delete folder {RESULTS_DIR}"
    raise Exception(err)

# Create directory where results will be stores
os.mkdir(RESULTS_DIR)

# Parse and Clean datasets
dataset = GetDatasets("datasets/", SINGLE_PAIR_MODE, ASSET1, ASSET2)

# Split data
train_data, test_data = train_test_split(dataset, test_size=TESTING_DATA_ALLOCATION, shuffle=False)

# Calculate and save Correlation Matrix
CorrelationMatrix(train_data, RESULTS_DIR)

# Calculate P-Values
pvalues, pairs = FindCointegratedPairs(train_data, PVALUE_THRESHOLD)
CointegrationPValues(pvalues, train_data, RESULTS_DIR)
if SINGLE_PAIR_MODE:
    pairs = [[ASSET1, ASSET2]]

# Final testing
for i in pairs:
    asset1 = i[0]
    asset2 = i[1]

    # Create Directory
    TEST_DIR = RESULTS_DIR + "/"+asset1+"_"+asset2
    os.mkdir(TEST_DIR)

    # create a train dataframe of 2 assets
    train = pd.DataFrame()
    train[asset1] = train_data[asset1]
    train[asset2] = train_data[asset2]

    # Regular prices
    Prices(asset1, asset2, train, TEST_DIR)

    # OLS regression
    model = sm.OLS(train[asset2], train[asset1]).fit()
    OLSRegression(str(model.summary()), TEST_DIR)

    # Spread
    spread = train[asset2] - model.params[0] * train[asset1]
    Spread(spread, TEST_DIR)

    # conduct Augmented Dickey-Fuller test - probability critical values
    adf = adfuller(spread, maxlag=1)
    print(f'{asset1} vs {asset2} Critical Value is {adf[0]}, while 1% is {adf[4]["1%"]}',)

    # Signals based on ZScore
    signals = ProduceZScoreTradingSignals(asset1, asset2, test_data, StdDevMul)
    Signals(asset1, asset2, signals, TEST_DIR)

    # Calculate Portfolio and its PNL
    portfolio = PortfolioPNL(TEST_DIR, asset1, asset2, signals, INIT_CAPITAL)

    # calculate CAGR
    final_portfolio = portfolio['total asset'].iloc[-1]
    delta = (portfolio.index[-1] - portfolio.index[0]).days

    YEAR_DAYS = 365
    returns = (final_portfolio / (INIT_CAPITAL*2)) ** (YEAR_DAYS / delta) - 1
    profit_stats = f'Number of days = {delta} with CAGR = {round(returns * 100, 2)}%'

    PortfolioPerformance(portfolio, TEST_DIR, profit_stats)

    plt.close()

print("Finished Cointegration Test")