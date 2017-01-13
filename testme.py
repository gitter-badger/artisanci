import artisan


class FakeWorker(object):
    def __init__(self):
        import os
        self.environment = os.environ.copy()
        self.cwd = os.getcwd()


command = artisan.LocalCommand(FakeWorker(), 'echo Hello!')
command.wait(timeout=1.0)
print(command.stdout.read(4))
print(command.stdout.read(4))
print(command.stdout.read(4))