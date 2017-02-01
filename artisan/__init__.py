""" Modern, flexible, and platform-agnostic interface for
automation, continuous integration, and farm management. """
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

__author__ = 'Seth Michael Larson'
__email__ = 'sethmichaellarson@protonmail.com'
__license__ = 'MIT'
__version__ = 'dev'

__all__ = [
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

    'RemoteWorkerAgent'
]
