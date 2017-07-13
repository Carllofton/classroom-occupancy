# Import models
import os
import json
import time
import pickle
import requests
import numpy as np
import pandas as pd

from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, RobustScaler

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
tscv = TimeSeriesSplit()
for train_index, test_index in tscv.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

# Create pipeline to scale the data and tune the model's hyperparameter: pipeline
pipeline = make_pipeline(RobustScaler(), KNeighborsClassifier())

# Setup parameter grid of possible n_neighbors values: param_grid
param_grid = {'kneighborsclassifier__n_neighbors': np.arange(1, 15)}

# Use GridSearchCV to find optimum number of n_neighbors: knn
knn = GridSearchCV(pipeline, param_grid=param_grid, cv=tscv)

# Fit the GridSearchCV object to the training data
knn.fit(X_train, y_train)

# Predict test set labels: y_pred
y_pred = knn.predict(X_test)

# Save fitted model to disk
pickle.dump(knn, open(knn_model, 'wb'))
