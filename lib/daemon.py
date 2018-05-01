import os
from signal import SIGTERM
import sys
import lib.custom_exceptions as ce
from lib.constants import Constants as const


def run(func, database):
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    if os.path.exists(const.PID_FILE):
        raise ce.DaemonAlreadyStarted
    with open(const.PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    func(database)


def stop():
    if os.path.exists(const.PID_FILE):
        with open(const.PID_FILE, 'r') as f:
            pid = int(f.read())
        os.remove(const.PID_FILE)
        os.kill(pid, SIGTERM)
    else:
        raise ce.DaemonIsNotStarted
