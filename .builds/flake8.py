from artisanci import Worker


def install(worker):
    assert isinstance(worker, Worker)
    worker.execute('python -m pip install flake8')
    worker.execute('flake8 --version')


def script(worker):
    assert isinstance(worker, Worker)
    worker.execute('flake8 setup.py artisan/')
