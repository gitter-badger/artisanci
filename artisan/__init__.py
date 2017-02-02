"""
      __        _______  ___________  __      ________     __      _____  ___
     /""\      /"      \("     _   ")|" \    /"       )   /""\    (\"   \|"  \
    /    \    |:        |)__/  \\__/ ||  |  (:   \___/   /    \   |.\\   \    |
   /' /\  \   |_____/   )   \\_ /    |:  |   \___  \    /' /\  \  |: \.   \\  |
  //  __'  \   //      /    |.  |    |.  |    __/  \\  //  __'  \ |.  \    \. |
 /   /  \\  \ |:  __   \    \:  |    /\  |\  /" \   :)/   /  \\  \|    \    \ |
(___/    \___)|__|  \___)    \__|   (__\_|_)(_______/(___/    \___)\___|\____\)

         `Open-Source Continuous Integration Services that work for you!`
                      Copyright (c) 2017 Seth Michael Larson

          _______________________ MIT License __________________________

          Permission is hereby granted, free of charge, to any person
          obtaining a copy of this software and associated documentation
          files (the "Software"), to deal in the Software without
          restriction, including without limitation the rights to use,
          copy, modify, merge, publish, distribute, sublicense, and/or
          sell copies of the Software, and to permit persons to whom the
          Software is furnished to do so, subject to the following
          conditions:

          The above copyright notice and this permission notice shall
          be included in all copies or substantial portions of the Software.

          THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
          EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
          OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
          NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
          BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
          ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
          CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
          SOFTWARE.
          ______________________________________________________________
"""
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
from .job import (Job,
                  JOB_STATUS_FAILURE,
                  JOB_STATUS_SUCCESS,
                  JOB_STATUS_ERROR,
                  JOB_STATUS_UNSTABLE,
                  JOB_STATUS_PENDING,
                  JOB_STATUS_RUNNING)
from .job_queue import JobQueue

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

    'RemoteWorkerAgent',

    'Job',
    'JOB_STATUS_RUNNING',
    'JOB_STATUS_PENDING',
    'JOB_STATUS_UNSTABLE',
    'JOB_STATUS_ERROR',
    'JOB_STATUS_FAILURE',
    'JOB_STATUS_SUCCESS',
    'JobQueue'
]
