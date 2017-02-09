from .base_executor import BaseExecutor
from .._vendor import virtualbox

__all__ = [
    'VirtualBoxExecutor'
]
_MINIMUM_VIRTUALBOX_SDK_VERSION = (5, 1, 14)


class VirtualBoxExecutor(BaseExecutor):
    """ :class:`artisan.executor.BaseExecutor` implementation
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
    def __init__(self, machine, workers=1):
        super(VirtualBoxExecutor, self).__init__(workers)
        self.machine = machine
        self._virtualbox = virtualbox.VirtualBox()

    def setup(self):
        vm = self._virtualbox.find_machine(self.machine)
        # TODO: Finish the rest of VirtualBoxExecutor.
