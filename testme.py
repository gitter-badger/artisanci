import os

from artisan import LocalBuilder
from artisan.job import LocalJob
from artisan.report import CommandLineReport

if __name__ == '__main__':
    j = LocalJob('tests', '.artisan/tests.py', os.path.dirname(os.path.abspath(__file__)))
    j.params['python'] = 'python3.5'
    j.report = CommandLineReport()
    b = LocalBuilder()
    b.build_job(j)
