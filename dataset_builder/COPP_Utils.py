import pandas as pd
import numpy as np

def appendFeature(base_df, ext_series, drop_col_name, fill_value = None):
  '''Concatenates a Series to a DataFrame. If after concatenating data
     the first row of a given day in ext_series is nan, it could be replaced
     by fill_value (as long as a fill_value is supplied). Right after that,
     a forward fill (ffill) is applied to the concatenated column.
     Also, after concatenating and ffilling, all rows containing nan in
     drop_col_name column will be deleted.'''
  fullset = pd.concat([base_df, ext_series], axis=1)
  fill_col_name = ext_series.name

  # Add a fill value at the beginning of given column, only if specified
  if fill_col_name != None:
    # extracting all the different dates (year/month/day) in the full dataset
    days = fullset.to_period('D').index.unique()

    # finding the mininum timestamp for each day in 'dates'.
    # this is used to assign a value of 0 people in the room at the beginning of each day,
    ## only if the value is null.
    for d in days:
      idx = fullset[d.strftime("%Y-%m-%d")].index.min()
      if pd.isnull(fullset.loc[idx,fill_col_name]):
        fullset.set_value(idx, fill_col_name, fill_value)

  # Forward fill only the changes of people count in the room
  fullset[fill_col_name] = fullset[fill_col_name].ffill()

  # then drop cases where there were no readings from the sensors (using only temperature it's enough)
  fullset.dropna(subset=[drop_col_name], inplace=True)

  return fullset

def replaceOutliers(df, mult=3):
  '''Replaces the outliers in a dataframe using a standard deviation multiplier.
     The default behaviour is to exclude all values greater than 3 stdevs'''
  res = df.copy()
  res[df.apply(lambda x: np.abs(x - x.mean()) > mult*x.std())] = np.nan
  return res.ffill().bfill()

def moving_average(a, n=15) :
  '''Regular moving average over a numpy array'''
  ret = np.cumsum(a, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n

def totalMA(a, n=15):
  '''Decrementing-window moving average to avoid losing data from initial
     points lower than the window. Works over a numpy array. Example:
     Having an array [1,2,3,4,5], a regular MA with n=4 will output
     [2.5, 3.5] while totalMA with n=4 will return [1.0, 1.5, 2.0, 2.5, 3.5],
     applying MAs of windows n= 3, 2 and 1 for values lower than the initial
     window of 4.'''
  tail = []
  for i in range(n-1):
    tail.append(np.mean(a[0:i+1]))
  tail.extend(moving_average(a, n))
  return tail

def interpolateByDay(df, tframe = '5S', useLast = False):
  '''Interpolate a set of days in a dataframe without adding any additional
     dead time. Instead of interpolating the entire dataset, it braks down
     the work by day and then concatenates everything back together.
     This is useful to prevent adding values before or after the first or
     last reading of a given day, but ensuring that  it will add missing
     values (through interpolation) inbetween the start and end dates.
     The default timeframe is 5 seconds.'''
  result = None
  days = df.to_period('D').index.unique()

  for d in days:
    aux = df[d.strftime("%Y-%m-%d")]
    # assigns NaN to new added values, then interpolate method will take
    # care of these blanks.
    # An alternate option for this method allows to resample using last seen
    # value in new timeframe.
    if (not useLast):
      aux = aux.resample(tframe).apply(lambda x: x.mean() if len(x) > 0 else np.nan)
    else:
      aux = aux.resample(tframe).last()

    # using pchip method to get a smoothed curve between initial and end points
    # of any previous gap.
    if (not useLast):
      aux = aux.interpolate(method='pchip')

    if result is None:
      result = aux
    else:
      result = pd.concat([result,aux])

  return result
