import spidev
import RPi.GPIO as GPIO
import time


class DoorSensor:
  def __init__(self, pin = None, verbose = False, dblogger = None):
    self.results = ()
    self.device = None
    self.pin = pin
    self.dblogger = dblogger
    self.verbose = verbose

    # assign default pin if none provided
    if self.pin == None:
      self.pin = 12

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    self.device = GPIO
    self.name = "Door"

  def getName(self):
    return self.name

  def door_event(self, open):
    evt = 'opened' if open else 'closed'
    self.results = (evt,)

    if open:
      if self.verbose: print('door ' + evt)
    else:
      if self.verbose: print('door ' + evt)

    time.sleep(0.5)

    # log in DB if logger present
    if self.dblogger is not None:
      self.logLastReading(self.dblogger)

  def waitForEvents(self):
    d = self.device
    pin = self.pin
    switch = True

    while True:
      if d.input(pin): # if door is opened
        if (switch):
          self.door_event(True) # send door open event
          switch = False # make sure it doesn't fire again
      if not d.input(pin): # if door is closed
        if not (switch):
          self.door_event(False) # send door closed event
          switch = True # make sure it doesn't fire again

  def logLastReading(self, dblogger):
    cursor = dblogger.cursor
    conn = dblogger.conn
    loc = dblogger.location
    tstamp = int(round(time.time() * 1000))
    cmd = "INSERT INTO Door (timestamp, location, door_status) VALUES (%s, %s, %s);"
    cursor.execute(cmd, (tstamp, loc, self.results[0]))
    conn.commit()

  def getLastReading(self):
    return self.results

  def cleanUp(self):
    GPIO.cleanup()

if __name__ == '__main__':
  # initialize different sensors
  vbose = True
  from ..DBLogger import DBLogger
  dbl = DBLogger()
  ds = DoorSensor(dblogger=dbl, verbose=vbose)

  # Listen to events
  try:
    ds.waitForEvents()
  except KeyboardInterrupt:
    if vbose: print("finishing.")
  finally:
    ds.cleanUp()
