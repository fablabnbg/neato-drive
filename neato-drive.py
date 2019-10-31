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

import time
import atexit

## this belongs all into class neato, but does not work there...
import termios, tty, sys, time
import serial

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

global_oldattr = None


class Neato():
  """
    Connect to a Neato Botvac, read the sensors control the motors.
  """

  __version__ = "0.2"


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


  def set_stdin_normal(self=None):
        global global_oldattr

        fd = sys.stdin.fileno()
        if global_oldattr is not None:
            ## hmm, why did we save global_oldattr? This should ave these bits already right. Apparently not...
            global_oldattr[tty.LFLAG] = global_oldattr[tty.LFLAG] | termios.ECHO | termios.ICANON | termios.IEXTEN
            termios.tcsetattr(fd, termios.TCSADRAIN, global_oldattr)


  def set_stdin_raw(self, timeout=0.1, fd=sys.stdin.fileno()):
        """ Set a character device in non-blocking one byte raw mode.
            The timeout is specified as a float [sec] here. For VTIME we convert to deciseconds.
            The filedescriptor defaults to stdin.
        """
        global global_oldattr

        global_oldattr = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)

        ## The bits are defined in the termios module, the bytes are in the tty module.
        # tty.IFLAG = 0
        # tty.OFLAG = 1
        # tty.CFLAG = 2
        # tty.LFLAG = 3
        # tty.ISPEED = 4
        # tty.OSPEED = 5
        # tty.CC = 6

        # VMIN defines the number of characters read at a time in
        # non-canonical mode. It seems to default to 1 on Linux, but on
        # Solaris and derived operating systems it defaults to 4. (This is
        # because the VMIN slot is the same as the VEOF slot, which
        # defaults to ASCII EOT = Ctrl-D = 4.)

        newattr[tty.LFLAG] = newattr[tty.LFLAG] & ~(termios.ECHO | termios.ICANON | termios.IEXTEN)
        newattr[tty.CC][termios.VMIN] = 0
        newattr[tty.CC][termios.VTIME] = int(10 * timeout + .5)

        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        return global_oldattr


  def fetchkey(self):
      """
      If the pressed key was a modifier key, nothing will be detected; if
      it were a special function key, it may return the first character of
      of an escape sequence, leaving additional characters in the buffer.
      """
      fd = sys.stdin.fileno()
      instr = ''
      self.set_stdin_raw(0.01, fd)
      # try:
      while True:
            input = sys.stdin.read(32)
            # print("input", input)
            if len(input) < 1:
              break
            instr += input
      ## not neeed here, atexit() does it all.
      # finally:
      #     self.set_stdin_normal()
      return instr


# --------------------------------------------------------------------------

if __name__ == '__main__':

  C_UP = '\x1b[A'
  C_DN = '\x1b[B'
  C_RE = '\x1b[C'
  C_LE = '\x1b[D'

  SHIFT_C_UP = '\x1b[1;2A'
  SHIFT_C_DN = '\x1b[1;2B'
  SHIFT_C_RE = '\x1b[1;2C'
  SHIFT_C_LE = '\x1b[1;2D'

  SHIFT_C_UP = '\x1b[1;5A'
  SHIFT_C_DN = '\x1b[1;5B'
  SHIFT_C_RE = '\x1b[1;5C'
  SHIFT_C_LE = '\x1b[1;5D'

  bot = Neato()

  atexit.register(bot.set_stdin_normal)

  vac = 40
  speed = 100

  bot.send("setmotor vacuumspeed 40 vacuumon")
  while True:
    inp = bot.fetchkey()

    if inp in [ 'q', 'Q' ]:
      bot.waitmotors()
      print("q")
      break

    elif inp in [ '+' ]:
      speed += 20
      if speed > 200: speed = 200
      print("+ (speed=%d)", speed)
      break

    elif inp in [ '-' ]:
      speed -= 20
      if speed < 10: speed = 10
      print("- (speed=%d)", speed)
      break

    elif inp in ( C_UP, 'w', 'k' ):
      print("C_UP")
      bot.send("setmotor speed %d LWheelDist 10 RWheelDist 10" % (speed))       # 1cm fwd
      # bot.waitmotors()
    elif inp in ( C_DN, 's', 'j' ):
      print("C_DN")
      bot.send("setmotor speed %d LWheelDist -10 RWheelDist -10" % (speed))      # 1cm bwd
      # bot.waitmotors()

    elif inp in ( C_RE, 'd', 'l'):
      print("C_RE")
      bot.send("setmotor speed 200 LWheelDist 30 RWheelDist 10" % (speed))         # 5 deg clockwise
      # bot.waitmotors()
    elif inp in ( C_LE, 'a', 'h' ):
      print("C_LE")
      bot.send("setmotor speed 200 LWheelDist 10 RWheelDist 30" % (speed))         # 5 deg counterclockwise
      # bot.waitmotors()

    elif inp in ( SHIFT_C_UP, 'K' ):
      print("SHIFT_C_UP")
      bot.send("setmotor speed 200 LWheelDist 100 RWheelDist 100" % (speed))      # 10cm fwd
      # bot.waitmotors()
    elif inp in ( SHIFT_C_DN, 'J' ):
      print("SHIFT_C_DN")
      bot.send("setmotor speed 200 LWheelDist 100 RWheelDist -100" % (speed))     # 10cm bwd
      # bot.waitmotors()

    elif inp in ( SHIFT_C_RE, 'L' ):
      print("SHIFT_C_RE")
      bot.send("setmotor speed 200 LWheelDist 196 RWheelDist -196" % (speed))      # 90 deg clockwise
      bot.waitmotors()
    elif inp in ( SHIFT_C_LE, 'H' ):
      print("SHIFT_C_LE")
      bot.send("setmotor speed 200 LWheelDist -196 RWheelDist 196" % (speed))      # 90 def counter clockwise
      bot.waitmotors()

    elif inp == 'v':
      vac += 20
      if vac > 100: vac = 0
      print("v %d" % vac)
      bot.send("setmotor vacuumspeed %d vacuumon" % vac)
    elif inp == 'V':
      vac = 0
      print("V 0")
      bot.send("setmotor vacuumoff")

  bot.send("setmotor vacuumoff")
  time.sleep(1)

