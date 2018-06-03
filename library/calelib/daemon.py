import os
import sys
import tempfile
from signal import SIGTERM
import shutil
from calelib.custom_exceptions import DaemonAlreadyStarted, DaemonIsNotStarted


class Daemon:
    """
    Instance that works in background
    :param pid_pid_path: pid file pid_path
    """
    @staticmethod
    def run(func, database, pid_path):
        """
        Run function as daemon
        :param pid_path:
        :param func: function to run in background
        :param database: argument of function
        """
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        try:
            if os.path.exists(Daemon._read_pid_from_file(pid_path)):
                raise DaemonAlreadyStarted
        except FileNotFoundError:
            open(pid_path, 'a').close()
        with tempfile.TemporaryFile('w') as f:
            f.write(str(os.getpid()))
        tmp = tempfile.NamedTemporaryFile()
        Daemon._write_to_file(tmp.name, str(os.getpid()))
        Daemon._write_to_file(pid_path, tmp.name)
        func(database)

    @staticmethod
    def _read_pid_from_file(pid_path):
        with open(pid_path, 'r') as file:
            return file.read()

    @staticmethod
    def _write_to_file(pid_path: str, value: str):
        with open(pid_path, 'w') as file:
            file.write(value)

    @staticmethod
    def stop(pid_path):
        """
        Stop daemon via PID
        """
        try:
            tmp_pid = Daemon._read_pid_from_file(pid_path)
        except FileNotFoundError:
            raise DaemonIsNotStarted
        try:
            with open(tmp_pid) as pid_file:
                pid = int(pid_file.read())
                os.kill(pid, SIGTERM)
        except (FileNotFoundError, ProcessLookupError):
            pass
        finally:
            os.remove(pid_path)

    @staticmethod
    def restart(func, database, pid_path):
        """
        Restart daemon
        :param pid_path:
        :param func: function to run in background
        :param database: argument of function
        """
        if os.path.exists(pid_path):
            stop(pid_path)
            run(func, database, pid_path)
