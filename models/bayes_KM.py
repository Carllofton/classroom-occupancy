# Import models
from urllib.request import urlretrieve
import numpy as np
import pandas as pd
import pickle

from sklearn.model_selection import TimeSeriesSplit
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder

# Data ingestion
URL = 'https://raw.githubusercontent.com/georgetown-analytics/classroom-occupancy/master/models/sensor_data_ml.csv'

def fetch_data(fname='sensor_data_ml.csv'):
    response = requests.get(URL)
    outpath = os.path.abspath(fname)
    with open(outpath, 'wb') as f:
        f.write(response.content)

    return outpath

DATA = fetch_data()

# Load sensor data as pandas dataframe with DateTimeIndex
df = pd.read_csv('sensor_data_ml.csv', index_col='datetime', parse_dates=True)

# Encode multiclass target variable
encoder = LabelEncoder()
encoder.fit_transform(df['occupancy_level'])

# Create features and target arrays
X = df.drop('occupancy_level', axis=1).values
y = df['occupancy_level']

# Use TimeSeriesSplit to create training and test indices
tscv = TimeSeriesSplit(n_splits=12)
for train_index, test_index in tscv.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

# Fit GaussianNB classifier onto the training data: bayes
bayes = GaussianNB().fit(X_train, y_train)

# Predict test set labels: y_pred
y_pred = bayes.predict(X_test)

# Save fitted model to disk
pickle.dump(bayes, open(bayes_model, 'wb'))
