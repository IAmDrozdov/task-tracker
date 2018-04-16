class User:
    def __init__(self, **kwargs):
        self.name = None
        self.tasks = []
        self.archive = []
        self.mail = None
        self.__dict__.update(**kwargs)