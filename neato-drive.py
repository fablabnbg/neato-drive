#!/usr/bin/python3
#
# (c) 2019 juergen@fabmail.org
# Distribute under GPLv2 or ask.
#
# Requires:
#  - apt-get install python3-serial
#  - apt-get install python3-pip
#  - pip3 install -U pip setuptools
#  - pip3 install evdev
#
# neato-drive.py
# V0.1		jw initial draught

import serial
import time

# getmotors
#  Parameter,Value
#  Brush_RPM,0
#  Brush_mA,0
#  Vacuum_RPM,0
#  Vacuum_mA,0
#  LeftWheel_RPM,900
#  LeftWheel_Load%,27
#  LeftWheel_PositionInMM,21733
#  LeftWheel_Speed,51
#  RightWheel_RPM,-900
#  RightWheel_Load%,32
#  RightWheel_PositionInMM,-1439
#  RightWheel_Speed,-52
#  ROTATION_SPEED,0.00
#  SideBrush_mA,0
# getmotors
#  Parameter,Value
#  Brush_RPM,0
#  Brush_mA,0
#  Vacuum_RPM,0
#  Vacuum_mA,0
#  LeftWheel_RPM,0
#  LeftWheel_Load%,0
#  LeftWheel_PositionInMM,22321
#  LeftWheel_Speed,0
#  RightWheel_RPM,0
#  RightWheel_Load%,0
#  RightWheel_PositionInMM,-2009
#  RightWheel_Speed,0
#  ROTATION_SPEED,0.00
#  SideBrush_mA,0



# b'getmotors\r\nParameter,Value\r\nBrush_RPM,0\r\nBrush_mA,0\r\nVacuum_RPM,4800\r\nVacuum_mA,404\r\nLeftWheel_RPM,3300\r\nLeftWheel_Load%,75\r\nLeftWheel_PositionInMM,28143\r\nLeftWheel_Speed,187\r\nRightWheel_RPM,-3600\r\nRightWheel_Load%,71\r\nRightWheel_PositionInMM,-3226\r\nRightWheel_Speed,-206\r\nROTATION_SPEED,0.00\r\nSideBrush_mA,0\r\n\x1a\r\n\x1a'
# b'setmotor speed 200 LWheelDist 196 RWheelDist -196\r\n\x1a\r\n\x1agetmotors\r\nParameter,Value\r\nBrush_RPM,0\r\nBrush_mA,0\r\nVacuum_RPM,3000\r\nVacuum_mA,255\r\nLeftWheel_RPM,3600\r\nLeftWheel_Load%,66\r\nLeftWheel_PositionInMM,28313\r\nLeftWheel_Speed,205\r\nRightWheel_RPM,3300\r\nRightWheel_Load%,18\r\nRightWheel_PositionInMM,-3205\r\nRightWheel_Speed,187\r\nROTATION_SPEED,0.00\r\nSideBrush_mA,0\r\n\x1a\r\n\x1a'
# b'getmotors\r\nParameter,Value\r\nBrush_RPM,0\r\nBrush_mA,0\r\nVacuum_RPM,4200\r\nVacuum_mA,466\r\nLeftWheel_RPM,3300\r\nLeftWheel_Load%,77\r\nLeftWheel_PositionInMM,28446\r\nLeftWheel_Speed,187\r\nRightWheel_RPM,-3300\r\nRightWheel_Load%,76\r\nRightWheel_PositionInMM,-3323\r\nRightWheel_Speed,-188\r\nROTATION_SPEED,0.00\r\nSideBrush_mA,0\r\n\x1a\r\n\x1a'
# b'setmotor speed 200 LWheelDist 196 RWheelDist -196\r\n\x1a\r\n\x1agetmotors\r\nParameter,Value\r\nBrush_RPM,0\r\nBrush_mA,0\r\nVacuum_RPM,5400\r\nVacuum_mA,426\r\nLeftWheel_RPM,3300\r\nLeftWheel_Load%,77\r\nLeftWheel_PositionInMM,28621\r\nLeftWheel_Speed,187\r\nRightWheel_RPM,3600\r\nRightWheel_Load%,16\r\nRightWheel_PositionInMM,-3295\r\nRightWheel_Speed,205\r\nROTATION_SPEED,0.00\r\nSideBrush_mA,0\r\n\x1a\r\n\x1a'


class Neato():
  """
    Connect to a Neato Botvac, read the sensors control the motors.
  """

  __version__ = "0.1"


  def send(self, text):
    self._ser.write(bytes(text + "\r\n", "ascii"))


  def waitready(self):
    time.sleep(0.4)
    a = self._ser.read(100)
    print(a)
    time.sleep(0.1)


  def waitmotors(self):
    for i in range(60):
      self.send("getmotors")
      time.sleep(0.4)
      a = self._ser.read(500)
      if b"LeftWheel_Speed,0" in a and b"RightWheel_Speed,0" in a:
        print("waitmotors: motors have stopped.")
        return True
      print(a)
      time.sleep(0.1)
    print("waitmotors: timed out after 30 sec.")
    return False


  def __init__(self, serial_port="/dev/ttyACM0"):
    self._ser = serial.Serial(serial_port, timeout=0.1)	# read timeout 100msec
    self.send("testmode on")
    self.waitready()

# --------------------------------------------------------------------------

if __name__ == '__main__':

  bot = Neato()

  for i in range(10):
    bot.send("setmotor vacuumspeed 40 vacuumon")
    for s in range(4):
      bot.send("setmotor speed 200 LWheelDist 1000 RWheelDist 1000")      # 1m fwd
      bot.waitmotors()
      bot.send("setmotor speed 200 LWheelDist 196 RWheelDist -196")       # 90 deg clockwise
      bot.waitmotors()
    bot.send("setmotor vacuumoff")
    time.sleep(2)

