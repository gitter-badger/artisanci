import os
from artisan.worker import BaseWorker


def install(worker):
    assert isinstance(worker, BaseWorker)
    worker.execute('python -m pip install -r dev-requirements.txt')
    worker.execute('python -m pip install .')
    worker.remove_directory(os.path.join('docs', '_build'))


def script(worker):
    assert isinstance(worker, BaseWorker)

    # make.bat must be in cwd on Windows.
    if worker.platform == 'Windows':
        worker.change_directory('docs')
    try:
        worker.execute('make html')
    finally:
        worker.change_directory('..')
