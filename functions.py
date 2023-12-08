import numpy as np
import pandas as pd
import os
from statsmodels.tsa.stattools import coint


def FindCointegratedPairs(data: pd.DataFrame, pval_threshold):
    n = data.shape[1]
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):

            # Equalize size
            new_df = data[[keys[i], keys[j]]].copy()
            new_df.dropna(inplace=True)

            # test for cointegration
            result = coint(new_df[keys[i]], new_df[keys[j]])
            p_value = result[1]
            pvalue_matrix[i, j] = p_value

            # filter out
            if p_value < pval_threshold:
                pairs.append((keys[i], keys[j]))
    return pvalue_matrix, pairs


def GetDatasets(path: str, single_mode, pair1, pair2):
    frame = pd.DataFrame
    ind = 0
    for i in os.listdir(path):
        if not i.endswith("xlsx"):
            continue
        name = i[:-5]

        if (name != pair1 and name != pair2) and single_mode:
            continue

        if ind == 0:
            ind = 1
            frame = pd.read_excel("datasets/" + i, thousands=",")
            frame.dropna(inplace=True)
            frame["Datetime"] = pd.to_datetime(frame["Date"])
            del frame["Date"]
            frame.set_index(["Datetime"], inplace=True)
            frame['Close'] = frame['Close'].astype(float)
            frame.rename(columns={"Close": name}, inplace=True)
        else:
            f = pd.read_excel("datasets/" + i, thousands=",")
            f.dropna(inplace=True)
            f["Datetime"] = pd.to_datetime(f["Date"])
            del f["Date"]
            f.set_index(["Datetime"], inplace=True)
            f['Close'] = f['Close'].astype(float)
            f.rename(columns={"Close": name}, inplace=True)

            frame = pd.merge(frame, f, left_index=True, right_index=True)

    frame.sort_index(inplace=True)
    return frame


def z_score(series):
    return (series - series.mean()) / np.std(series)


def ProduceZScoreTradingSignals(asset1, asset2, data, stdev_mul):
    signals = pd.DataFrame()
    signals[asset1] = data[asset1]
    signals[asset2] = data[asset2]
    ratios = signals[asset1] / signals[asset2]
    # calculate z-score and define upper and lower thresholds
    signals['z'] = z_score(ratios)
    signals['z upper limit'] = np.mean(signals['z']) + np.std(signals['z']) * stdev_mul
    signals['z lower limit'] = np.mean(signals['z']) - np.std(signals['z']) * stdev_mul
    # create signal - short if z-score is greater than upper limit else long
    signals['signals1'] = 0
    signals['signals1'] = np.select([signals['z'] > signals['z upper limit'], signals['z'] < signals['z lower limit']],
                                    [-1, 1], default=0)
    # we take the first order difference to obtain portfolio position in that stock
    signals['positions1'] = signals['signals1'].diff()
    signals['signals2'] = -signals['signals1']
    signals['positions2'] = signals['signals2'].diff()
    return signals

def longProfit(shares, entry_price, current_price):
    return current_price * shares - entry_price * shares

def shortProfit(shares, entry_price, current_price):
    return entry_price * shares - current_price * shares

def PortfolioPNL(path, asset1, asset2, signals:pd.DataFrame, initial_capital):
    # shares to buy for each position
    # since there are two assets, we calculate each asset Pnl separately
    # and in the end we aggregate them into one portfolio
    position = 0

    shares1 = 0
    entry_price1 = 0
    cash1 = initial_capital

    shares2 = 0
    entry_price2 = 0
    cash2 = initial_capital

    tradingLog = pd.DataFrame(columns=["Date", "Asset", "TradeType", "Price", "Size", "Side", "Profit"])
    result = pd.DataFrame()
    result[asset1] = signals[asset1]
    for i, data in signals.iterrows():
        current_price1 = data[asset1]
        current_price2 = data[asset2]

        if data["signals1"] == 1 and position != 1:
            if position == -1:
                # Close short position
                profit1 = shortProfit(shares1, entry_price1, current_price1)
                cash1 += profit1
                tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset1, "TradeType": "exit", "Side": "buy",
                                                   "Price": current_price1, "Size": shares1, "Profit": profit1}
                # Close long position
                profit2 = longProfit(shares2, entry_price2, current_price2)
                cash2 += profit2
                tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset2, "TradeType": "exit", "Side": "sell",
                                                   "Price": current_price2, "Size": shares2, "Profit": profit2}

            cash1 = (cash1 + cash2) / 2
            cash2 = cash1
            # Open Long Position
            entry_price1 = current_price1
            shares1 = round(cash1 / entry_price1)
            tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset1, "TradeType": "entry", "Side": "buy",
                                               "Price": entry_price1, "Size": shares1, "Profit": 0}
            # Open Short Position
            entry_price2 = current_price2
            shares2 = round(cash2 / entry_price2)
            tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset2, "TradeType": "entry", "Side": "sell",
                                               "Price": entry_price2, "Size": shares2, "Profit": 0}
            position = 1

        elif data["signals1"] == -1 and position != -1:
            if position == 1:
                # Close long position
                profit1 = longProfit(shares1, entry_price1, current_price1)
                cash1 += profit1
                tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset1, "TradeType": "exit", "Side": "sell",
                                                   "Price": current_price1, "Size": shares1, "Profit": profit1}
                # Close short position
                profit2 = shortProfit(shares2, entry_price2, current_price2)
                cash2 += profit2
                tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset2, "TradeType": "exit", "Side": "buy",
                                                   "Price": current_price2, "Size": shares2, "Profit": profit2}
            cash1 = (cash1 + cash2) / 2
            cash2 = cash1
            # Open Short
            entry_price1 = current_price1
            shares1 = round(cash1 / entry_price1)
            tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset1, "TradeType": "entry", "Side": "sell",
                                               "Price": entry_price1, "Size": shares1, "Profit": 0}
            # Open Long
            entry_price2 = current_price2
            shares2 = round(cash2 / entry_price2)
            tradingLog.loc[len(tradingLog)] = {"Date": i, "Asset": asset2, "TradeType": "entry", "Side": "buy",
                                               "Price": entry_price2, "Size": shares2, "Profit": 0}
            position = -1

        if position == -1:
            # result["total asset1"] =
            profit1 = cash1 + shortProfit(shares1, entry_price1, current_price1)
            profit2 = cash2 + longProfit(shares2, entry_price2, current_price2)
            result.loc[i, "total asset"] = profit1 + profit2
        elif position == 1:
            profit1 = cash1 + longProfit(shares1, entry_price1, current_price1)
            profit2 = cash2 + shortProfit(shares2, entry_price2, current_price2)
            result.loc[i, "total asset"] = profit1 + profit2
        else:
            result.loc[i, "total asset"] = cash1 + cash2

    tradingLog.to_excel(path + "/trading_log.xlsx")
    # total pnl and z-score
    result['z'] = signals['z']
    result['z upper limit'] = signals['z upper limit']
    result['z lower limit'] = signals['z lower limit']
    result = result.dropna()

    return result