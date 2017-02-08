""" Definition of the BaseJob interface. """

#           Copyright (c) 2017 Seth Michael Larson
# _________________________________________________________________
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import threading
from .exceptions import JobFailureException, JobErrorException

JOB_STATUS_PENDING = 'pending'
JOB_STATUS_RUNNING = 'running'
JOB_STATUS_SUCCESS = 'success'
JOB_STATUS_FAILURE = 'failure'
JOB_STATUS_ERROR = 'error'
JOB_STATUS_UNSTABLE = 'unstable'

_JOB_STATUSES_COMPLETED = set([JOB_STATUS_SUCCESS,
                               JOB_STATUS_FAILURE,
                               JOB_STATUS_UNSTABLE,
                               JOB_STATUS_ERROR])

__all__ = [
    'Job',

    'JOB_STATUS_FAILURE',
    'JOB_STATUS_ERROR',
    'JOB_STATUS_PENDING',
    'JOB_STATUS_SUCCESS',
    'JOB_STATUS_RUNNING',
    'JOB_STATUS_UNSTABLE'
]


class Job(threading.Thread):
    def __init__(self):
        self.worker = None
        self.status = JOB_STATUS_PENDING
        self.exception = None
        self.artifacts = {}

        self._callbacks = []

        super(Job, self).__init__()

    def run(self):
        """ Helper method that is used by scheduling
        jobs for a worker."""
        self.status = JOB_STATUS_RUNNING
        try:
            result = self.execute(self.worker)
            if result in _JOB_STATUSES_COMPLETED:
                self.status = result
            else:
                self.status = JOB_STATUS_SUCCESS
        except JobFailureException as e:
            self.exception = e
        except Exception as e:
            self.exception = JobErrorException(e)
        if self.exception is not None:
            self.status = JOB_STATUS_ERROR

        for func, args, kwargs in self._callbacks:
            func(self, *args, **kwargs)

    def add_callback(self, func, *args, **kwargs):
        """
        Add a function to call after the job is completed.
        Will be called immediately if the job is already completed.

        :param func: Function to call with the job as the only parameter.
        """
        if self.status in _JOB_STATUSES_COMPLETED:
            func(self, *args, **kwargs)
        else:
            self._callbacks.append((func, args, kwargs))

    def execute(self, worker):
        raise NotImplementedError()
