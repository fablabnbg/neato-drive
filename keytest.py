#! /usr/bin/python3
#
# https://www.programcreek.com/python/example/836/termios.tcsetattr
# https://docs.python.org/3/library/termios.html

import termios, tty, sys, select
import time
import atexit

global_oldattr = None


def set_stdin_raw(timeout=0.1, fd=sys.stdin.fileno()):
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


def set_stdin_normal():
        global global_oldattr

        fd = sys.stdin.fileno()
        if global_oldattr is not None:
            ## hmm, why did we save global_oldattr? This should ave these bits already right. Apparently not...
            global_oldattr[tty.LFLAG] = global_oldattr[tty.LFLAG] | termios.ECHO | termios.ICANON | termios.IEXTEN
            termios.tcsetattr(fd, termios.TCSADRAIN, global_oldattr)


def fetchkey():
      """
      If the pressed key was a modifier key, nothing will be detected; if
      it were a special function key, it may return the first character of
      of an escape sequence, leaving additional characters in the buffer.
      """
      fd = sys.stdin.fileno()
      instr = ''
      set_stdin_raw(0.01, fd)
      # try:
      while True:
            input = sys.stdin.read(32)
            # print("input", input)
            if len(input) < 1:
              break
            instr += input
      ## not neeed here, atexit() does it all.
      # finally:
      #     set_stdin_normal()
      return instr


## Support normal-terminal reset at exit
atexit.register(set_stdin_normal) 

while True:
  c = fetchkey()
  if len(c):
    print("seen: ", [ c ])
    if c[0] == 'q':
      break



