class BaseService:
    def execute(self):
        raise NotImplementedError

    def __call__(self):
        return self.execute()
