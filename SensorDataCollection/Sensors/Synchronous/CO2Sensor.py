import serial
import time

class CO2Sensor:
  def __init__(self, serialf = ""):
    self.results = ()
    self.serialf = serialf
    self.device = None

    # assign default serial file if none provided
    if self.serialf == "":
      self.serialf = "/dev/ttyS0"

    ser = serial.Serial(self.serialf)
    ser.write("K 2\r\n")
    ser.flushInput()
    time.sleep(1)

    self.device = ser
    self.name = "CO2"

  def getName(self):
    return self.name


  def getNewReading(self):
    d = self.device
    d.write("Z\r\n")
    time.sleep(.01)
    resp = d.read(10)
    resp = resp[:8]
    fltCo2 = float(resp[2:])
    time.sleep(0.2)
    self.results = (fltCo2,)
    return self.results

  def logLastReading(self, dblogger, time_id):
    cursor = dblogger.cursor
    conn = dblogger.conn
    loc = dblogger.location
    cmd = "INSERT INTO CO2 (rel_stamp, location, co2) VALUES (%s, %s, %s);"
    cursor.execute(cmd, (time_id, loc, self.results[0]))
    conn.commit()


  def getLastReading(self):
    return self.results

  def cleanUp(self):
    pass
