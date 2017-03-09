""" Script that can be used to run Artisan CI
test suite using the current build of Artisan CI. :)

This is the equivalent of ``artisanci --type local`` """

import os
from artisanci import LocalBuilder
from artisanci.builds import LocalBuild
from artisanci.reporters import BasicCommandLineReporter

if __name__ == '__main__':
    l = LocalBuilder()
    builds = []
    for script in ['.builds/tests.py', '.builds/docs.py', '.builds/flake8.py']:
        b = LocalBuild(script, 5.0, path=os.getcwd())
        b.add_watcher(BasicCommandLineReporter())
        l.execute_build(b)
        builds.append(b)
    for b in builds:
        b.wait()
