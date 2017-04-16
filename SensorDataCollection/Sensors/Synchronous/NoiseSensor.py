import spidev
import time


class NoiseSensor:
  def __init__(self, channel = None):
    self.results = ()
    self.device = None
    self.channel = channel

    # assign default channel if none provided
    if self.channel == None:
      self.channel = 0

    spi = spidev.SpiDev()
    spi.open(0,0)


    self.device = spi
    self.name = "Noise"

  def getName(self):
    return self.name

  def getNewReading(self):
    d = self.device
    chn = self.channel

    #check for valid channel
    if ( (chn > 7) or (chn < 0) ):
      return -1
    # Preform SPI transaction and store returned bits in 'r'
    r = d.xfer( [1, (8 + chn) << 4, 0] )
    # Filter data bits from returned bits
    val = ( (r[1] & 3) << 8 ) + r[2]

    self.results = (val,)
    return self.results

  def logLastReading(self, dblogger, time_id):
    cursor = dblogger.cursor
    conn = dblogger.conn
    loc = dblogger.location
    cmd = "INSERT INTO Noise (rel_stamp, location, noise) VALUES (%s, %s, %s);"
    cursor.execute(cmd, (time_id, loc, self.results[0]))
    conn.commit()

  def getLastReading(self):
    return self.results

  def cleanUp(self):
    self.device.close()

if __name__ == '__main__':
    # initialize different sensors
  ns = NoiseSensor()

  for i in range(10):
    print(ns.getNewReading())
    time.sleep(1)

  ns.cleanUp()
