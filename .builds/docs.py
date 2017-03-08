import os
from artisanci import Worker


def install(worker):
    assert isinstance(worker, Worker)
    worker.execute('python -m pip install -r dev-requirements.txt')
    worker.execute('python -m pip install .')
    if worker.isdir(os.path.join('docs', '_build')):
        worker.remove(os.path.join('docs', '_build'))


def script(worker):
    assert isinstance(worker, Worker)
    worker.chdir('docs')
    worker.execute('make html')
