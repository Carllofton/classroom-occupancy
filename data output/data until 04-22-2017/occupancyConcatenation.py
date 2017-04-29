import pandas as pd
import numpy as np
from datetime import datetime

# auxiliar method to find the closest timestamp in a list to a given date
def nearest(tstamps, date):
    return min(tstamps, key=lambda x: abs(x - date))

if __name__ == '__main__':
  occ = pd.read_csv('occupancy_data.csv')
  sen  = pd.read_csv('sensor_data.csv')

  # converting sensor time strings to timestamps
  sen.datetime = pd.to_datetime(sen.datetime)
  # converting occupancy time strings to timestamps
  occ.datetime = pd.to_datetime(occ.datetime)

  # keep only last seen record for every different second
  occ.drop_duplicates(subset='datetime', keep='last', inplace=True)

  occ = occ.set_index('datetime')
  sen = sen.set_index('datetime')
  
  fullset = pd.concat([sen, occ], axis=1)

  # extracting all the different dates (year/month/day) in the full dataset
  dates = np.unique(occ.index.map(lambda t: t.strftime('%Y-%m-%d')))
  
  # deleting irrelevant columns
  del fullset['location']
  del fullset['count_operation']
  del fullset['count_change']
  
  # finding the mininum timestamp for each day in 'dates'.
  # this is used to assign a value of 0 people in the room at the beginning of each day,
  ## only if the value is null.
  for d in dates:
    id = nearest(fullset.index,datetime.strptime(d, '%Y-%m-%d'))
    row = fullset.ix[id]
    if pd.isnull(row.count_total):
      fullset.set_value(id, 'count_total', 0)

  # Forward fill only the changes of people count in the room
  fullset.count_total = fullset.count_total.ffill()
  
  # then drop cases where there were no readings from the sensors (using only temperature it's enough)
  fullset.dropna(subset=['temperature'], inplace=True)
  
  # export
  fullset.to_csv('dataset.csv')
  
  print('process completed.')