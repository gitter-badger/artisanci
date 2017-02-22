from artisan import Worker


def install(worker):
    assert isinstance(worker, Worker)
    worker.execute('python -m pip install -r dev-requirements.txt')
    worker.execute('python -m pip install .')


def script(worker):
    assert isinstance(worker, Worker)
    worker.execute('nosetests -v tests/')


def after_success(worker):
    assert isinstance(worker, Worker)
    worker.execute('codecov --env ARTISAN_BUILD_ID,ARTISAN_JOB_ID')
