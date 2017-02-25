
import semver
from .base_builder import BaseBuilder
from .virtualbox_pool import MachinePool
from .._vendor import virtualbox
from ..exceptions import ArtisanException

__copyright__ = """
          Copyright (c) 2017 Seth Michael Larson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific
language governing permissions and limitations under the License.
"""

__all__ = [
    'VirtualBoxBuilder'
]
_MINIMUM_VIRTUALBOX_SDK_VERSION = '5.1.14'


class VirtualBoxBuilder(BaseBuilder):
    """ :class:`artisan.builder.BaseExecutor` implementation
    that uses VirtualBox in order to create a secure environment
    for untrusted tests to execute in.

     .. warning::

        The following steps should be taken in order to secure your
        VirtualBox Virtual Machine. Without all these steps your
        machine may be vulnerable and will only allow the Executor
        to be used for non-public operations.

        - Setup NAT Networking with a forwarding rule to access 80 and 443.
        - Have a non-'null' Remote Desktop Authentication method.
        - Disable clipboard sharing.
        - Disable shared folders.
        - Disable 3D graphics acceleration.
        - Disable CD/DVD pass-through.
        - Disable USB pass-through.
        - Disable Drag-and-Drop.

        The following steps are recommended and if not taken may leave your
        Virtual Machine potentially vulnerable:

        - Disable Page Fusion.
        - Do not run Windows versions older than Vista with Service Pack 1.

        In addition to these steps make sure to always update your VirtualBox
        and Guest Additions to their latest versions. Artisan will error if
        an insecure version of VirtualBox is being used.

        These steps are taken from the `Virtual Box Manual Chapter 13
        <https://www.virtualbox.org/manual/ch13.html>`_.
    """
    def __init__(self, machine, username, password, python, builders=1):
        super(VirtualBoxBuilder, self).__init__(python=python, builders=builders)
        self.machine = machine
        self.username = username
        self.password = password

        self._pool = None
        self._session = None

        manager = virtualbox.Manager()
        vbox = manager.get_virtualbox()

        if not semver.match(vbox.version_normalized,
                            '>=' + _MINIMUM_VIRTUALBOX_SDK_VERSION):
            fmt = (vbox.version_normalized,
                   _MINIMUM_VIRTUALBOX_SDK_VERSION)
            raise ArtisanException('VirtualBox API detected as version `%s`. '
                                   'Artisan requires at least version `%s` or '
                                   'above. Please upgrade your VirtualBox.' % fmt)

    def setup(self, job):
        self._pool = MachinePool(self.machine)
        self._session = self._pool.acquire()

    def execute(self, job):
        import time
        time.sleep(60.0)

    def teardown(self, job):
        if self._pool is not None:
            if self._session is not None:
                self._pool.release(self._session)
                self._session = None
            self._pool = None
