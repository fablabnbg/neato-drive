#! /usr/bin/python3
#
# https://www.programcreek.com/python/example/836/termios.tcsetattr
# https://docs.python.org/3/library/termios.html

import termios, tty, sys, select
import time

global_oldattr = None
global_tty_fd = None


def set_term_raw(timeout=0.1, fd=sys.stdin.fileno()):
        """ Set a character device in non-blocking one byte raw mode.
            The timeout is specified as a float [sec] here. For VTIME we convert to deciseconds.
            The filedescriptor defaults to stdin.
        """
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

        newattr[tty.LFLAG] = newattr[tty.LFLAG] & ~termios.ICANON & ~termios.ECHO
        newattr[tty.LFLAG] = newattr[tty.LFLAG] & ~(termios.ECHO | termios.ICANON | termios.IEXTEN)
        newattr[tty.CC][termios.VMIN] = 1
        newattr[tty.CC][termios.VMIN] = 1
        newattr[tty.CC][termios.VTIME] = int(10 * timeout + .5)

        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        global_tty_fd = fd
        return global_oldattr


def set_stdin_normal():
        fd = sys.stdin.fileno()
        if global_oldattr is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, global_oldattr)


def fetchkey():
      """
      If the pressed key was a modifier key, nothing will be detected; if
      it were a special function key, it may return the first character of
      of an escape sequence, leaving additional characters in the buffer.
      """
      fd = sys.stdin.fileno()
      ch = None
      set_term_raw(0.1, fd)
      try:
          ch = sys.stdin.read(1)
      finally:
          set_stdin_normal()
      return ch

while True:
  c = fetchkey()
  if c:
    print("seen: ", c)
    if c[0] == 'q':
      break


## Support normal-terminal reset at exit
# atexit.register(set_stdin_normal) 

