# Import models
import os
import json
import time
import pickle
import requests
import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.svm import SVC

# Data ingestion
URL = 'https://raw.githubusercontent.com/georgetown-analytics/classroom-occupancy/master/models/sensor_data_ml.csv'

def fetch_data(fname='sensor_data_ml.csv'):
    response = requests.get(URL)
    outpath = os.path.abspath(fname)
    with open(outpath, 'wb') as f:
        f.write(response.content)

    return outpath

DATA = fetch_data()

# Load sensor data as pandas dataframe with DateTimeIndex: df
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

# Create pipeline to scale the data and tune the model's hyperparameter: pipe
pipe = make_pipeline(RobustScaler(), SVC())

# Specify the hyperparameter space
param_range = [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.00]

param_grid = [{'clf__kernel': ['linear'], 'clf__C': param_range, 'clf__class_weight': [None, 'balanced']}, {'clf__kernel': ['rbf'], 'clf__C': param_range, 'clf__class_weight': [None, 'balanced'], 'clf__gamma': param_range}]

grid = GridSearchCV(pipe, param_grid, cv=tscv)

# Fit the pipeline to the training data: svc
svc = grid.fit(X_train, y_train)

# Predict the test set labels: y_pred
y_pred = svc.predict(X_test)

# Save the fitted model to disk
svc_model = 'svc_model.sav'

# Save fitted model to disk
pickle.dump(logreg_clf, open(svc_model, 'wb'))
