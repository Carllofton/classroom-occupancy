import argparse
import threading
from multiprocessing import Process
import os
from datetime import datetime
from timeit import default_timer as timer
from time import sleep, strftime
from Sensors.DBLogger import DBLogger
from Sensors.Synchronous.THSensor import THSensor
from Sensors.Synchronous.CO2Sensor import CO2Sensor
from Sensors.Synchronous.BTSensor import BTSensor
from Sensors.Synchronous.LuxSensor import LuxSensor
from Sensors.Synchronous.NoiseSensor import NoiseSensor
from Sensors.Asynchronous.DoorSensor import DoorSensor

def getSensorReading(sensor, verbose, sync=True):
  if sync:
    r = sensor.getNewReading()
    if verbose: print("reading for {}: {}".format(sensor.getName(), '(' + ', '.join(format(f, '.2f') for f in r) + ')'))
  else:
    try:
      sensor.waitForEvents()
    except KeyboardInterrupt:
      if verbose: print("[{}-SENSOR] stopping and cleaning subprocess.".format(sensor.getName().upper()))
    finally:
      sensor.cleanUp()

def spawnAndStartThread(args_, tname):
  th = threading.Thread(target=getSensorReading, args=args_, name=tname)
  th.start()
  return th

def spawnThemAll(sensors, verbose=True):
  threads = []

  for s in sensors:
    t = spawnAndStartThread((s,verbose,), s.getName())
    threads.append(t)

  return threads

def getReadings(sensors):
  reads = []

  for s in sensors:
    reads.append(s.getLastReading())

  return reads

def joinThemAll(threads):
  for t in threads:
    # join at most for 30 secs
    t.join(30)

def cleanThemAll(sensors):
  for s in sensors:
    s.cleanUp()

def logReadingsInCSV(sensors):
  reads = getReadings(sensors)
  reporttime = (strftime("%Y-%m-%d %H:%M:%S"))
  csvresult = open("results.csv","a")
  csvresult.write(reporttime + "," + ''.join(str(e) for e in reads) + "\n")
  csvresult.close

def logReadingsInDB(sensors, dbl, tstamp):
  for s in sensors:
    s.logLastReading(dbl, tstamp)

def initArgs():
  parser = argparse.ArgumentParser(description='Reads from several sensors and logs values into MySQL database.')
  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='show fetched values in stdout for every iteration.')
  parser.add_argument("-i", '--iter-seconds', type=float, default=5.0, help='seconds to wait before a new reading iteration executes.')
  parser.add_argument("-l", '--location', default='Georgetown', help='location where the sensors are taking data from. As this project originally started in a Georgetown classroom, the default is "Georgetown".')

  args = parser.parse_args()

  return (args.verbose, args.iter_seconds, args.location)

if __name__ == '__main__':
  # initialize arguments
  args = initArgs()
  # whether we want to print readings to the console
  verbose = args[0]
  # seconds to sleep after every iteration
  waitTime = args[1]
  # location to use for database records
  location = args[2]
  # control variables for sleep time
  end, start = waitTime, 0

  # initialize different sensors
  sensors = [THSensor(), CO2Sensor(), BTSensor(), LuxSensor(), NoiseSensor()]
  # initialize DB Logger with given location from arguments
  dblog = DBLogger(location)

  try:
    # run asynchronous sensors without waiting for them
    ds = DoorSensor(verbose=verbose, dblogger=dblog)
    p = Process(target=getSensorReading, args=(ds,verbose,False))
    p.start()

    # read from all sensors until interrupted
    while True:
      start = timer()
      if (verbose): print("\n---iteration at {}---".format(datetime.now()))

      # timestamp shared accross every sensor reading in the database, for every iteration
      iter_time = datetime.now()

      # start reading every sensor independently
      threads = spawnThemAll(sensors, verbose)

      # wait for every thread to finish reading its sensor calues
      joinThemAll(threads)

      # Log all values in database after every sensor is read.
      logReadingsInDB(sensors, dblog, iter_time)

      end = timer()

      # wait until an aproximation of 'waitTime is met
      while (end - start < waitTime):
        sleep(0.0005)
        end = timer()
      if (verbose): print("----------duration: {:0.6f} seconds---------".format(end - start))

  except KeyboardInterrupt:
    print("\n\nprocess stopped.")

  finally:
    print("cleaning...")
    cleanThemAll(sensors)
    dblog.cleanUp()
    print("ok, see ya!")
