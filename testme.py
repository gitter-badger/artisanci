from artisan import VirtualBoxBuilder
from artisan.job import GitJob

if __name__ == '__main__':
    j = GitJob('t', '.artisan/tests.py', 'https://github.com/SethMichaelLarson/artisan.git', 'master')
    b = VirtualBoxBuilder('ubuntu-14.04', 'artisan-builder', 'artisan-builder', '/usr/bin/python')
    b.build_job(j)
