import os
import time
import uuid
from .base_builder import BaseBuilder
from .._vendor import virtualbox

__all__ = [
    'VirtualBoxBuilder'
]
_MINIMUM_VIRTUALBOX_SDK_VERSION = (5, 1, 14)


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
    def __init__(self, machine, python):
        super(VirtualBoxBuilder, self).__init__(python)
        self.machine = machine

        manager = virtualbox.Manager()
        self._virtualbox = manager.get_virtualbox()
        self._machine = self._virtualbox.find_machine(self.machine)
        self._session = manager.get_session()
        self._snapshot = None

    def setup(self, job):
        progress = self._machine.launch_vm_process(self._session, 'gui', '')
        progress.wait_for_completion(10000)
        if progress.result_code != 0:
            raise ValueError('Timeout!')

        self._snapshot = uuid.uuid4().hex
        self._session.machine.take_snapshot(self._snapshot, '', False)

        print(self._machine.find_snapshot(self._snapshot).__uuid__)
        guest = self._session.console.guest.create_session('test', 'test')
        while True:
            time.sleep(5.0)
            try:
                guest.execute(self.python, ['--version'])
                break
            except Exception:
                pass

    def execute(self, job):
        pass

    def teardown(self, job):
        snapshot_file = os.path.join(self._session.machine.snapshot_folder, self._session)
        try:
            progress = self._session.console.power_down()
            progress.wait_for_completion(10000)
        except Exception:
            pass
        if self._snapshot is not None:
            try:
                snapshot = self._machine.find_snapshot(self._snapshot)
                progress = self._session.machine.restore_snapshot(snapshot)
                progress.wait_for_completion(10000)
            except Exception:
                pass
        self._session = None
        self._machine = None
        self._virtualbox = None
