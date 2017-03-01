import unittest
import artisan
from tests.const import VIRTUALBOX_INSTALLED


@unittest.skipUnless(VIRTUALBOX_INSTALLED, 'Must have VirtualBox installed to run these tests.')
class TestVirtualBox(unittest.TestCase):
    def test_virtualbox_launch(self):
        builder = artisan.VirtualBoxBuilder('test', 'artisan-builder', 'artisan-builder', '/usr/bin/python')
        builder.execute(None)
