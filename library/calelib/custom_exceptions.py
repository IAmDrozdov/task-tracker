class DaemonAlreadyStarted(Exception):
    pass


class DaemonIsNotStarted(Exception):
    pass


class CycleError(Exception):
    pass
