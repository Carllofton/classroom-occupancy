#!/usr/bin/python

from PIL import Image, ImageChops
import math, operator
from functools import reduce
import pandas as pd
from datetime import datetime
from collections import OrderedDict
from glob import glob
from os import walk

def rmsdiff(im1, im2):
  """Calculate the root-mean-square difference between two images"""
  h = ImageChops.difference(im1, im2).histogram()
  # calculate rms
  return math.sqrt(reduce(operator.add, map(lambda h, i: h*(i**2), h, range(256))) / (float(im1.size[0]) * im1.size[1]))

def rollingDiff(imgs):
  diffs = [0]
  for i1, i2 in zip(imgs, imgs[1:]):
    diffs.append(rmsdiff(i1, i2))
  return diffs

def controlDiff(control, imgs):
  diffs = []
  for i in imgs:
    diffs.append(rmsdiff(control, i))
  return diffs

def loadImgs(dir ="./"):
  dic =  {}
  img_names = glob(dir+"*.jpg")
  for n in img_names:
    dt = datetime.strptime(n[:-7], dir+'still-%Y-%m-%d_%H.%M')
    dic[dt] = Image.open(n)
  return OrderedDict(sorted(dic.items(), key=lambda t: t[0]))

def parseImages(foldername='', basedir='.'):
  imgsDict = loadImgs(basedir+foldername+'/')
  imgs = list(imgsDict.values())
  keys = imgsDict.keys()

  print(basedir+foldername+'/', '*'*40)

  rolling = rollingDiff(imgs)

  first_img = imgsDict[min(keys)]
  last_img = imgsDict[max(keys)]
  control_first = controlDiff(first_img, imgs)
  control_last = controlDiff(last_img, imgs)

  df = pd.DataFrame(
    {'datetime': list(keys),
     'rolling_rms': rolling,
     'control_F_rms': control_first,
     'control_L_rms': control_last
    })
  df.set_index('datetime', inplace=True)
  print(df)

  name = ('output' if foldername == '.' else 'img_var-' + foldername) + '.csv'
  print('\nexporting as:', name)
  df.to_csv(name)
  print('-'*10)

def parseDirectory(basedir='.'):
  dirs = next(walk(basedir))[1]
  print('parsing {} directories..'.format(len(dirs)))
  for d in dirs:
    parseImages(d, basedir = basedir)
  print('\n\nDONE.')

if __name__ == '__main__':
  parseDirectory('/home/abraham/Desktop/class pictures backup/sub/')
