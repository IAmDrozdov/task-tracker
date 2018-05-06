import os
import sys
import tempfile
from signal import SIGTERM

import calendoola_app.lib.custom_exceptions as ce
from calendoola_app.lib.constants import Constants as const


def run(func, database):
    """
    Run function as daemon
    :param func: function to run in background
    :param database: argument of function
    """
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    try:
        if os.path.exists(read_from_file(const.PID_PATH_FILE)):
            raise ce.DaemonAlreadyStarted
    except FileNotFoundError:
        open(const.PID_PATH_FILE, 'a').close()
    with tempfile.TemporaryFile('w') as f:
        f.write(str(os.getpid()))
    tmp = tempfile.NamedTemporaryFile()
    write_to_file(tmp.name, str(os.getpid()))
    write_to_file(const.PID_PATH_FILE, tmp.name)
    func(database)


def read_from_file(path: str):
    with open(path, 'r') as file:
        return file.read()


def write_to_file(path: str, value: str):
    with open(path, 'w') as file:
        file.write(value)


def stop():
    """
    Stop daemon via PID
    """
    pid_path = read_from_file(const.PID_PATH_FILE)
    try:
        with open(pid_path) as pid_file:
            pid = int(pid_file.read())
            os.kill(pid, SIGTERM)
    except FileNotFoundError:
        pass
    finally:
        os.remove(const.PID_PATH_FILE)


def restart(func, database):
    """
    Restart daemon
    :param func: function to run in background
    :param database: argument of function
    """
    if os.path.exists(const.PID_PATH_FILE):
        stop()
        run(func, database)
