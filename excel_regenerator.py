import pandas as pd
import json
import os

# Parse settings
with open("settings.json", "r") as f:
    settings = json.load(f)
    # Define INIT variables
    PATH = settings["PathToExcelFileWithData"]
    df = pd.read_excel(PATH)


dataframes = []
index = 1
for i in df.columns:
    if not index % 3:
        del df[i]
    index += 1

index = 1
for i in df.columns:
    if index % 2 != 0:
        new_frame = pd.DataFrame()
        new_frame[i] = df[i]
    else:
        new_frame[i] = df[i]
        new_frame
        dataframes.append(new_frame)
    index += 1

if not os.path.exists("datasets"):
    os.mkdir("datasets")

for i in dataframes:
    name = "datasets/" + i.columns[0] + ".xlsx"
    if os.path.exists(name):
        continue
    i.rename(columns={i.columns[0]: "Date", i.columns[1]: "Close"}, inplace=True)
    i.drop(0, inplace=True)
    i.to_excel(name, index=False)