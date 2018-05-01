import os
from signal import SIGTERM
import sys
import lib.custom_exceptions as ce


def run(func, database):
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    if os.path.exists('pid'):
        raise ce.DaemonAlreadyStarted
    with open('pid', 'w') as f:
        f.write(str(os.getpid()))
    func(database)


def stop():
    if os.path.exists('pid'):
        with open('pid', 'r') as f:
            pid = int(f.read())
        os.remove('pid')
        os.kill(pid, SIGTERM)
    else:
        raise ce.DaemonIsNotStarted
