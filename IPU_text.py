
import sys
from tty import setraw
from termios import tcsetattr, tcgetattr, TCSADRAIN

user_input = ''


# def read_char():
#     fd = sys.stdin.fileno()
#     old_settings = tcgetattr(fd)
#     setraw(sys.stdin.fileno())
#     global user_input
#     user_input = ''
#     while user_input != 'q':
#         user_input = sys.stdin.read(1)
#         if user_input == 'f':
#             sys.stdout.write("\rHaHaHa!!!")
#             sys.stdout.flush()
#         sys.stdout.write("\r%s" % user_input)
#         sys.stdout.flush()
#     tcsetattr(fd, TCSADRAIN, old_settings)
#     sys.stdout.write("\n")
#     return user_input

def read_char():
    fd = sys.stdin.fileno()
    old_settings = tcgetattr(fd)
    setraw(sys.stdin.fileno())
    global user_input
    user_input = ''
    try:
        while user_input != 'q':
            try:
                user_input = sys.stdin.read(1)
                if user_input == 'f':
                    sys.stdout.write("\rHaHaHa!!!")
                    sys.stdout.flush()
                sys.stdout.write("\r%s" % user_input)
                sys.stdout.flush()
            except IOError:
                pass
    finally:
        tcsetattr(fd, TCSADRAIN, old_settings)
        sys.stdout.write("\n")
    return user_input



read_char()
