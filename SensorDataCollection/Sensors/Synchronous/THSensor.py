import pigpio
import DHT22
import time

class THSensor:
  def __init__(self,gpio=0):
    self.results = ()
    self.gpio = gpio
    self.device = None
    self.pi = pigpio.pi()
    # assign default pin if none provided
    if self.gpio == 0:
      self.gpio = 22
    self.device = DHT22.sensor(self.pi, self.gpio)
    self.name = "THS"

  def getName(self):
    return self.name

  def getNewReading(self):
    d = self.device
    d.trigger()
    time.sleep(0.2)
    self.results = (d.temperature(), d.humidity())

    return self.results

  def getLastReading(self):
    return self.results

  def logLastReading(self, dblogger, time_id):
    cursor = dblogger.cursor
    conn = dblogger.conn
    loc = dblogger.location
    cmd = "INSERT INTO Temp_and_humidity (rel_stamp, location, temperature, humidity) VALUES (%s, %s, %s, %s);"
    cursor.execute(cmd, (time_id, loc, self.results[0], self.results[1]))
    conn.commit()

  def cleanUp(self):
    self.device.cancel()
    self.pi.stop()

if __name__ == '__main__':
    # initialize different sensors
  ths = THSensor()

  for i in range(3):
    print(ths.getNewReading())
    time.sleep(1.5)

  ths.cleanUp()
