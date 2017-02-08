import platform
from .base_service import BaseService
if platform.system == 'Windows':
    from .windows_service import WindowsService as DefaultService
else:
    from .posix_service import PosixService as DefaultService

__all__ = [
    'BaseService',
    'DefaultService'
]
