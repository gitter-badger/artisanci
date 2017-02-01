""" Modern, flexible, and platform-agnostic interface for
automation, continuous integration, and farm management. """
from .worker.command import (BaseCommand,
                             LocalCommand,
                             SshCommand,
                             RemoteCommand)

from .exceptions import (JobTimeoutException,
                         JobErrorException,
                         JobFailureException,
                         JobCancelledException,
                         CommandExitStatusException,
                         CommandTimeoutException,
                         WorkerNotAvailable,
                         IncorrectPassword,
                         OperatingSystemError,
                         OperationNotSupported)
from .remote_agent import RemoteWorkerAgent
from .worker import (FileAttributes,
                     BaseWorker,
                     LocalWorker,
                     SshWorker,
                     RemoteWorker)

__author__ = 'Seth Michael Larson'
__email__ = 'sethmichaellarson@protonmail.com'
__license__ = 'MIT'
__version__ = 'dev'

__all__ = [
    'BaseCommand',
    'LocalCommand',
    'SshCommand',
    'RemoteCommand',

    'JobTimeoutException',
    'JobCancelledException',
    'JobFailureException',
    'JobErrorException',
    'CommandTimeoutException',
    'CommandExitStatusException',
    'WorkerNotAvailable',
    'IncorrectPassword',
    'OperatingSystemError',
    'OperationNotSupported',

    'FileAttributes',
    'BaseWorker',
    'LocalWorker',
    'SshWorker',
    'RemoteWorker',

    'RemoteWorkerAgent'
]
