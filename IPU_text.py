
import sys
from tty import setraw
from termios import tcsetattr, tcgetattr, TCSADRAIN


def read_char():
    fd = sys.stdin.fileno()
    old_settings = tcgetattr(fd)
    setraw(sys.stdin.fileno())
    user_input = ''
    while user_input != 'q':
        user_input = sys.stdin.read(1)
        sys.stdout.write("\r%s" % user_input)
        sys.stdout.flush()
    tcsetattr(fd, TCSADRAIN, old_settings)
    sys.stdout.write("\n")
    return user_input

read_char()
