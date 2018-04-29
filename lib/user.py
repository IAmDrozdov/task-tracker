class User:
    def __init__(self, **kwargs):
        self.nickname = None
        self.tasks = []
        self.plans = []
        self.archive = []
        self.__dict__.update(kwargs)
