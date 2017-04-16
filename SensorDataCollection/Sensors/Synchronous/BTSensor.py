import bluetoothctl
import time

class BTSensor:
  def __init__(self):
    self.results = ()
    self.device = None

    bl = bluetoothctl.Bluetoothctl()
    bl.start_scan()
    self.device = bl
    self.name = "BT"

  def getName(self):
    return self.name


  def getNewReading(self):
    d = self.device
    devs = d.get_discoverable_devices()
    
    not_pers = 0
    for d in devs:
      if d['name'] == d['mac_address'].replace(":", "-"):
        not_pers += 1

    dev_count = len(devs)

    self.results = (dev_count, not_pers)
    return self.results

  def logLastReading(self, dblogger, time_id):
    cursor = dblogger.cursor
    conn = dblogger.conn
    loc = dblogger.location
    cmd = "INSERT INTO Bluetooth (rel_stamp, location, devices, np_devices) VALUES (%s, %s, %s, %s);"
    cursor.execute(cmd, (time_id, loc, self.results[0], self.results[1]))
    conn.commit()


  def getLastReading(self):
    return self.results

  def cleanUp(self):
    pass
