import unittest
import mock
from artisan import VirtualBoxBuilder
from artisan.exceptions import ArtisanSecurityException
from artisan._vendor import virtualbox
from artisan.builder.virtualbox_builder import _MINIMUM_VIRTUALBOX_VERSION


class TestVirtualBoxBuilderSecurity(unittest.TestCase):
    def check_raises_security_exception(self):
        self.assertRaises(ArtisanSecurityException, VirtualBoxBuilder, 'test', 'artisan-builder', 'artisan-builder',
                          '/usr/bin/python')

    @mock.patch.object(virtualbox, 'VirtualBox')
    def test_outdated_virtualbox_version(self, mock_vbox):
        vbox = mock.Mock()
        mock_vbox.return_value = vbox

        vbox.version_normalized = '5.1.13'

        self.check_raises_security_exception()

    @mock.patch.object(virtualbox, 'VirtualBox')
    def test_page_fusion_enabled(self, mock_vbox):
        vbox = mock.Mock()
        vbox.version_normalized = _MINIMUM_VIRTUALBOX_VERSION
        mock_vbox.return_value = vbox

        mock_machine = mock.Mock()
        vbox.find_machine.return_value = mock_machine
        mock_machine.page_fusion_enabled = True

        self.check_raises_security_exception()
