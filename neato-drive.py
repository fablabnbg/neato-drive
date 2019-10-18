#!/usr/bin/python3
#
# (c) 2019 juergen@fabmail.org
# Distribute under GPLv2 or ask.
#
# Requires:
#  sudp apt-get install python3-serial
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



def waitmotors():
  for i in range(60):
    ser.write(b"getmotors\r\n")
    time.sleep(0.4)
    a = ser.read(500)
    if b"LeftWheel_Speed,0" in a and b"RightWheel_Speed,0" in a:
      return True
    print(a)
    time.sleep(0.1)
  print("waitmotors: timed out after 30 sec.")
  return False

def waitready():
  time.sleep(0.4)
  a = ser.read(100)
  print(a)
  time.sleep(0.1)

   
ser = serial.Serial('/dev/ttyACM0', timeout=0.2)	# read timeout 200msec
ser.write(b"testmode on\r\n")
waitready()

for i in range(10):
  ser.write(b"setmotor vacuumspeed 40 vacuumon\r\n")
  for s in range(4):
    ser.write(b"setmotor speed 200 LWheelDist 1000 RWheelDist 1000\r\n")	# 1m fwd
    waitready()
    ser.write(b"setmotor speed 200 LWheelDist 196 RWheelDist -196\r\n")	# 90 deg clockwise
    waitready()
  ser.write(b"setmotor vacuumoff\r\n")
  time.sleep(2) 


