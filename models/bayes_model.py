import os
from urllib.request import urlopen, urlretrieve
import numpy as np
import pandas as pd

# Data Ingestion
url = 'https://raw.githubusercontent.com/georgetown-analytics/classroom-occupancy/master/models/sensor_updated_ml.csv'
urlretrieve(url, 'sensor_updated_ml.cvs')

# Sensor Data
df = pd.read_csv('sensor_updated_ml.csv', index_col='datetime', parse_dates=True)

# Rename columns
df.columns = ['temp', 'humidity', 'co2', 'light', 'light_st', 'noise', 'bluetooth', 'images', 'door', 'occupancy_count']

# Create target column 'occupancy_level'
df['occupancy_level'] = pd.cut(df['occupancy_count'], [0, 1,16, 27, 40], labels=['empty', 'low', 'mid-level', 'high'], include_lowest=True)

# Encode multi-class labels
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
encoder.fit(['empty', 'low', 'mid-level', 'high']).transform(df.occupancy_level)

# Create features and target arrays
X = df.drop('occupancy_level', axis=1).values
y = df['occupancy_level'].values

# Use TimeSeriesSplit function to create training and test Data
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=12)

for train_index, test_index in tscv.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

# Fit GaussianNB classifer onto the data
from sklearn.naive_bayes import GaussianNB

bayes = GaussianNB().fit(X,y)

y_pred = bayes.predict(X_test)

# Save model to disk
import pickle

bayes_model = 'bayes_model.sav'
pickle.dump(bayes, open(bayes_model, 'wb'))
