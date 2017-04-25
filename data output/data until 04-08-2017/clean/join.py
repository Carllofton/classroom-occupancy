import pandas as pd

csv1 = pd.read_csv('sensor_data.csv')
csv2 = pd.read_csv('occupancy_data.csv')
merged = csv1.merge(csv2, on="datetime", how="outer").fillna("")
merged.to_csv("output1.csv", index=False)
