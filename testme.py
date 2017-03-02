import os

from artisan import LocalBuilder
from artisan.job import LocalJob
from artisan.report import CommandLineReport

if __name__ == '__main__':
    jobs = []
    p = os.path.dirname(os.path.abspath(__file__))

    j = LocalJob('docs', '.artisan/docs.py', p)
    j.params['python'] = 'python'
    jobs.append(j)

    j = LocalJob('flake8', '.artisan/flake8.py', p)
    j.params['python'] = 'python'
    jobs.append(j)

    j = LocalJob('tests-python2.7', '.artisan/tests.py', p)
    j.params['python'] = 'python2.7'
    jobs.append(j)

    j = LocalJob('tests-python3.5', '.artisan/tests.py', p)
    j.params['python'] = 'python3.5'
    jobs.append(j)

    b = LocalBuilder()
    for j in jobs:
        j.report = CommandLineReport()
        b.build_job(j)
