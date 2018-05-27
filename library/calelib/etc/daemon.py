import os
import sys
import tempfile
from signal import SIGTERM

from calelib.etc.custom_exceptions import DaemonAlreadyStarted, DaemonIsNotStarted


class Daemon:

    def __init__(self, pid_path):
        """
        Instance that works in background
        :param pid_path: pid file path
        """
        self.path = pid_path

    def run(self, func, database):
        """
        Run function as daemon
        :param func: function to run in background
        :param database: argument of function
        """
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        try:
            if os.path.exists(self.__read_pid_from_file()):
                raise DaemonAlreadyStarted
        except FileNotFoundError:
            open(self.path, 'a').close()
        with tempfile.TemporaryFile('w') as f:
            f.write(str(os.getpid()))
        tmp = tempfile.NamedTemporaryFile()
        self.__write_to_file(tmp.name, str(os.getpid()))
        self.__write_to_file(self.path, tmp.name)
        func(database)

    def __read_pid_from_file(self):
        with open(self.path, 'r') as file:
            return file.read()

    @staticmethod
    def __write_to_file(path: str, value: str):
        with open(path, 'w') as file:
            file.write(value)

    def stop(self):
        """
        Stop daemon via PID
        """
        try:
            pid_path = self.__read_pid_from_file()
        except FileNotFoundError:
            raise DaemonIsNotStarted
        try:
            with open(pid_path) as pid_file:
                pid = int(pid_file.read())
                os.kill(pid, SIGTERM)
        except FileNotFoundError:
            pass
        finally:
            os.remove(self.path)

    def restart(self, func, database):
        """
        Restart daemon
        :param func: function to run in background
        :param database: argument of function
        """
        if os.path.exists(self.path):
            self.stop()
            self.run(func, database)
