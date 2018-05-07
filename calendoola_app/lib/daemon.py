import os
import sys
import tempfile
from signal import SIGTERM

import calendoola_app.lib.custom_exceptions as ce


class Daemon:

    def __init__(self, path):
        self.path = path

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
            if os.path.exists(self.read_from_file()):
                raise ce.DaemonAlreadyStarted
        except FileNotFoundError:
            open(self.path, 'a').close()
        with tempfile.TemporaryFile('w') as f:
            f.write(str(os.getpid()))
        tmp = tempfile.NamedTemporaryFile()
        self.write_to_file(tmp.name, str(os.getpid()))
        self.write_to_file(self.path, tmp.name)
        func(database)

    def read_from_file(self):
        with open(self.path, 'r') as file:
            return file.read()

    @staticmethod
    def write_to_file(path: str, value: str):
        with open(path, 'w') as file:
            file.write(value)

    def stop(self):
        """
        Stop daemon via PID
        """
        pid_path = self.read_from_file()
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
