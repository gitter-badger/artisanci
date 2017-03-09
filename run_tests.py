""" Script that can be used to run Artisan CI
test suite using the current build of Artisan CI. :)

This is the equivalent of ``artisanci --type local`` """

import os
from artisanci import VirtualBoxBuilder
from artisanci.builds import LocalBuild
from artisanci.reporters import BasicCommandLineReporter

if __name__ == '__main__':
    l = VirtualBoxBuilder('ubuntu-14.04', 'artisan-builder', 'artisan-builder', '/usr/bin/python')
    for script in ['.builds/tests.py', '.builds/docs.py', '.builds/flake8.py']:
        b = LocalBuild(script, path=os.getcwd())
        b.add_watcher(BasicCommandLineReporter())
        l.build_job(b)
