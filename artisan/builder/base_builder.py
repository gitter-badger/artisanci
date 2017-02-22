__all__ = [
    'BaseBuilder'
]


class BaseBuilder(object):
    """ Interface for Executors which setup and teardown the
    environment that a worker executes a job inside of. """
    def __init__(self, python):
        self.python = python
        self.busy = False

        # This flag, if `True`, will allow the
        # builder to have a public schedule.
        # Setting this flag as `True` for a non-secure
        # environment is strongly discouraged.
        self.is_secure = False

    def run(self, job):
        try:
            self.busy = True
            self.setup(job)
            self.execute(job)
        finally:
            self.busy = False
            self.teardown(job)

    def execute(self, job):
        raise NotImplementedError()

    def setup(self, job):
        raise NotImplementedError()

    def teardown(self, job):
        raise NotImplementedError()
