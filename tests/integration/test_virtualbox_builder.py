import subprocess
import os
import unittest
import artisan


def has_virtualbox():
    if os.environ.get('VIRTUALBOX', 'false') == 'true':
        return True
    else:
        try:
            subprocess.check_call(['VBoxManage', '-v'], timeout=3.0)
            return True
        except Exception:
            return False


@unittest.skipUnless(has_virtualbox(), 'Must have VirtualBox installed to run these tests.')
class TestVirtualBox(unittest.TestCase):
    def test_virtualbox_launch(self):
        builder = artisan.VirtualBoxBuilder('test', 'artisan-builder', 'artisan-builder', '/usr/bin/python')
        builder.execute(None)
