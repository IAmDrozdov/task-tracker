import json
from task import Task


class Encoder(json.JSONEncoder):
    """
    if type of serializable object is 'Task', encoder return dict with
    fields of this object
    """
    def default(self, py_object):
        if isinstance(py_object, Task):
            return py_object.__dict__
        raise TypeError(repr(py_object) + ' is not JSON serializable')
