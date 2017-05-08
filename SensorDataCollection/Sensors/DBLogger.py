import datetime
import MySQLdb
from os import sys

class DBLogger:
  def __init__(self, loc='default-location'):
    self.usr = '<user>'
    self.pwd = '<password>'
    self.dbase = '<database>'
    self.location = loc
    self.conn = MySQLdb.connect(host="localhost", user=self.usr, passwd=self.pwd, db=self.dbase)
    self.cursor = self.conn.cursor()

  def cleanUp(self):
    self.conn.close()
    self.cursor.close()
