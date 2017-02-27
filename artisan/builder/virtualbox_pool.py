
from contextlib import contextmanager
import random
import string
import time
from .._vendor.virtualbox import VirtualBox, Session
from .._vendor.virtualbox.library import CleanupMode
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

    def acquire(self, frontend='gui'):
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
