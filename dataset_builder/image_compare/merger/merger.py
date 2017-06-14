import pandas as pd
from glob import glob

if __name__ == '__main__':
  csvs = sorted(glob('../parsed_data/img_var-*.csv'))
  print(csvs)
  dfs = []
  for csv in csvs:
    dfs.append(pd.read_csv(csv, index_col='datetime'))

  all = dfs[0]
  iterdfs = iter(dfs)
  next(iterdfs)
  for df in iterdfs:
    all = all.append(df)

  print(all)
  print('\nexporting..')
  all.to_csv('image_variations.csv')
