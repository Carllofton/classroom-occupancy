import RPi.GPIO as GPIO
import time

class LuxSensor:
  def __init__(self,gpio=0):
    self.results = ()
    self.gpio = gpio
    self.device = None

    GPIO.setmode(GPIO.BOARD)
    # assign default pin if none provided
    if self.gpio == 0:
      self.gpio = 31

    # Output on the pin for initialization
    GPIO.setup(self.gpio, GPIO.OUT)
    GPIO.output(self.gpio, GPIO.LOW)
    time.sleep(0.2)

    # Change the pin back to input
    GPIO.setup(self.gpio, GPIO.IN)

    self.device = GPIO
    self.name = "Lux"

  def getName(self):
    return self.name


  def getNewReading(self):
    d = self.device

    # Output on the pin for initialization
    d.setup(self.gpio, GPIO.OUT)
    d.output(self.gpio, GPIO.LOW)
    time.sleep(0.2)

    # Change the pin back to input
    d.setup(self.gpio, GPIO.IN)

    # Count until the pin goes high
    count = 0
    while (d.input(self.gpio) == GPIO.LOW):
      count += 1

    self.results = (count,)

    return self.results

  def logLastReading(self, dblogger, time_id):
    cursor = dblogger.cursor
    conn = dblogger.conn
    loc = dblogger.location
    cmd = "INSERT INTO Light (rel_stamp, location, light) VALUES (%s, %s, %s);"
    cursor.execute(cmd, (time_id, loc, self.results[0]))
    conn.commit()


  def getLastReading(self):
    return self.results

  def cleanUp(self):
    GPIO.cleanup()

if __name__ == '__main__':
  lxs = LuxSensor()

  for i in range(3):
    print(lxs.getNewReading())

  lxs.cleanUp()
