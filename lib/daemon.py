import os
import sys
from signal import SIGTERM

import lib.custom_exceptions as ce
from lib.constants import Constants as const


def run(func, database):
    """
    Run function as daemon
    :param func: function to run in background
    :param database: argument of function
    """
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    if os.path.exists(const.PID_FILE):
        raise ce.DaemonAlreadyStarted
    with open(const.PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    func(database)


def stop():
    """
    Stop daemon via PID
    """
    if os.path.exists(const.PID_FILE):
        with open(const.PID_FILE, 'r') as f:
            pid = int(f.read())
        os.remove(const.PID_FILE)
        os.kill(pid, SIGTERM)
    else:
        raise ce.DaemonIsNotStarted


def restart(func, database):
    """
    Restart daemon
    :param func: function to run in background
    :param database: argument of function
    """
    if os.path.exists(const.PID_FILE):
        stop()
        run(func, database)
