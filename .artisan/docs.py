import os
from artisan import Worker


def install(worker):
    assert isinstance(worker, Worker)
    worker.execute('python -m pip install -r dev-requirements.txt')
    worker.execute('python -m pip install .')
    worker.remove_directory(os.path.join('docs', '_build'))


def script(worker):
    assert isinstance(worker, Worker)

    # make.bat must be in cwd on Windows.
    if worker.platform == 'Windows':
        worker.change_directory('docs')
    worker.execute('make html')
