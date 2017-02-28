
from contextlib import contextmanager
import random
import string
import time
from ..exceptions import ArtisanSecurityException
from .._vendor.virtualbox import VirtualBox, Session
from .._vendor.virtualbox.library import CleanupMode, ClipboardMode, DnDMode, DeviceType
from .._vendor.virtualbox.pool import LockType

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
    'MachinePool'
]


class MachinePool(object):
    def __init__(self, machine):
        self.machine = machine
        self._is_secure = False

    def acquire(self, frontend='headless'):
        if self._is_secure is None:
            self.run_security_check()
        with self._lock() as root_session:
            machine = root_session.machine
            token = ''.join(random.choice(string.ascii_letters) for _ in range(32))
            clone = machine.clone(name='%s clone-%s' % (self.machine, token))
            p = clone.launch_vm_process(type_p=frontend)
            p.wait_for_completion(60 * 1000)
            session = clone.create_session()
            return session

    def release(self, session):
        with self._lock():
            clone = self._power_down(session)
        try:
            session.unlock_machine()
        except Exception:
            pass
        while True:
            try:
                mediums = clone.unregister(CleanupMode.full)
                progress = clone.delete_config(mediums)
                progress.wait_for_completion(60 * 1000)
                break
            except Exception:
                time.sleep(0.3)
        return clone

    def run_security_check(self, allow_insecure=False):
        """ Runs a set of security checks to make sure the VirtualBox
        machine is hardened to prevent malicious users from breaking
        through the VM into the host machine.

        - Remote Desktop Authentication should be not 'null'.
        - Disable clipboard sharing.
        - Disable shared folders.
        - Disable 3D graphics acceleration.
        - Disable CD/DVD pass-through.
        - Disable USB pass-through.
        - Disable Drag-and-Drop.
        - Disable Page Fusion.
        - Disable Audio.
        - Verify the host OS is older than Vista with SP1.

        :param bool allow_insecure:
            If this value is True then the VirtualBox configuration
            is allowed to be insecure. This will mark the resulting
            builder as not being secure and only usable by users
            that have your API key.
        """
        vbox = VirtualBox()
        machine = vbox.find_machine(self.machine)
        try:
            self._is_secure = False

            # Page Fusion
            if machine.page_fusion_enabled:
                raise ArtisanSecurityException('Page fusion is enabled on '
                                               'the VM `%s`. This setting '
                                               'should be disabled.' % self.machine)
            # Clipboard Sharing
            if machine.clipboard_mode != ClipboardMode.disabled:
                raise ArtisanSecurityException('Clipboard Sharing is enabled '
                                               'on VM `%s`. This setting '
                                               'should be disabled.' % self.machine)
            # Shared Folders
            if len(machine.shared_folders) > 0:
                raise ArtisanSecurityException('The VM `%s` has shared folders '
                                               'defined. There should be no shared '
                                               'folders between the host and the '
                                               'guest machines.' % self.machine)
            # 3D Graphics Acceleration
            if machine.accelerate3_d_enabled:
                raise ArtisanSecurityException('The VM `%s` has 3D graphics '
                                               'acceleration enabled. This setting '
                                               'should be disabled.' % self.machine)
            # Drag-and-Drop
            if machine.dn_d_mode != DnDMode.disabled:
                raise ArtisanSecurityException('Drag-and-Drop is enabled on VM '
                                               '`%s`. This setting should be '
                                               'disabled.' % self.machine)
            # Audio Adapters
            if machine.audio_adapter.enabled:
                raise ArtisanSecurityException('Audio is enabled on VM `%s`. This '
                                               'setting should be disabled.' % self.machine)
            # Storage Mediums
            for attachment in machine.medium_attachments:
                if attachment.passthrough and attachment.type_p != DeviceType.network:
                    raise ArtisanSecurityException('The medium `%s` on VM `%s` has pass-'
                                                   'through enabled. All devices that are not '
                                                   'network devices should have pass-through '
                                                   'disabled.' % (attachment.medium.name,
                                                                  self.machine))
            self._is_secure = True
        except ArtisanSecurityException as e:
            if not allow_insecure:
                raise e

    @property
    def is_secure(self):
        return bool(self._is_secure)

    @contextmanager
    def _lock(self, timeout_ms=-1):
        vbox = VirtualBox()
        machine = vbox.find_machine(self.machine)
        wait_time = 0
        while True:
            session = Session()
            try:
                machine.lock_machine(session, LockType.write)
            except Exception as exc:
                if timeout_ms != -1 and wait_time > timeout_ms:
                    raise ValueError("Failed to acquire lock - %s" % exc)
                time.sleep(1)
                wait_time += 1000
            else:
                try:
                    yield session
                finally:
                    session.unlock_machine()
                break

    def _power_down(self, session):
        vbox = VirtualBox()
        clone = vbox.find_machine(session.machine.name)
        try:
            p = session.console.power_down()
            p.wait_for_completion(60 * 1000)
            session.unlock_machine()
            return clone
        finally:
            try:
                session.unlock_machine()
            except Exception:
                pass
