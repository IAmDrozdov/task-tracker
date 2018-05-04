class UserAlreadyExist(Exception):
    pass


class UserNotFound(Exception):
    pass


class UserNotAuthorized(Exception):
    pass


class PlanNotFound(Exception):
    pass


class TaskNotFound(Exception):
    pass


class DaemonAlreadyStarted(Exception):
    pass


class DaemonIsNotStarted(Exception):
    pass
