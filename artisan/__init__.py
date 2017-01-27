""" Modern, flexible, and platform-agnostic interface for
automation, continuous integration, and farm management. """
from .command import (BaseCommand,
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
                         OperatingSystemError)
from .worker import (FileAttributes,
                     BaseWorker,
                     LocalWorker,
                     SshWorker,
                     RemoteWorker)
from .remote_agent import RemoteWorkerAgent

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

    'FileAttributes',
    'BaseWorker',
    'LocalWorker',
    'SshWorker',
    'RemoteWorker',

    'RemoteWorkerAgent'
]
