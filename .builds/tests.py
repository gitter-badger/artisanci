from artisanci import Worker


def install(worker):
    assert isinstance(worker, Worker)
    worker.execute('python -m pip install -r dev-requirements.txt')
    worker.execute('python -m pip install .')


def script(worker):
    assert isinstance(worker, Worker)
    worker.execute('nosetests tests/unit/ tests/integration/', merge_stderr=True)
    worker.execute('coverage combine')
    worker.execute('coverage html')


def after_success(worker):
    assert isinstance(worker, Worker)
    if worker.environment.get('ARTISAN_BUILD_TRIGGER', 'manual') != 'manual':
        worker.execute('codecov --env ARTISAN_BUILD_ID')
