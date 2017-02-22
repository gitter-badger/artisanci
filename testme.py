from artisan import LocalBuilder, VirtualBoxBuilder
from artisan.job import LocalJob
from artisan.report import CommandLineReport


if __name__ == '__main__':
    e = VirtualBoxBuilder('ubuntu-14.04', 'artisan-builder', 'artisan-builder', '/usr/bin/python')
    for j in [LocalJob('.artisan/flake8', '.')]:
        j.report = CommandLineReport()
        e.run(j)
