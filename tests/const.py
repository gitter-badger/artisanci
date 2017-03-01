import subprocess

__all__ = [
    'VIRTUALBOX_INSTALLED'
]

try:
    subprocess.check_call(['VBoxManage', '-v'], timeout=3.0)
    VIRTUALBOX_INSTALLED = True
except Exception:
    VIRTUALBOX_INSTALLED = False
