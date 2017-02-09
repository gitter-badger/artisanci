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

import enum
import tarfile
import zipfile
from .worker import BaseWorker

__all__ = [
    'Job',
    'JobStatus',
    'JobProcess'
]


class JobStatus(enum.Enum):
    """ Enum for descripting the status of a job. """
    PENDING = 'pending'
    INSTALLING = 'install'
    RUNNING = 'running'
    CLEANUP = 'cleanup'
    SUCCESS = 'success'
    FAILURE = 'failure'
    ERROR = 'error'


class JobProcess(enum.Enum):
    # Clones the exact branch into the worker
    # and runs the script that is given.
    GITHUB = 'github'
    BITBUCKET = 'bitbucket'
    GITLAB = 'gitlab'

    # Makes an HTTP request to download a tar or zip file
    # and extracts the contents and runs the script.
    ARCHIVE = 'archive'


class Job(object):
    def __init__(self, process, path, params):
        self.status = JobStatus.PENDING
        self.process = process
        self.params = params
        self.path = path

    def run_process(self, worker):
        assert isinstance(worker, BaseWorker)
        path = worker.pathlib

        # Clear out a workspace for the worker.
        workspace = path.join(worker.home, 'workspace')
        if worker.is_directory(workspace):
            worker.remove_directory(workspace)
        worker.create_directory(workspace)

        if self.process == JobProcess.ARCHIVE:
            self.setup_archive_workspace(worker, workspace)
        elif self.process == JobProcess.GITHUB:
            self.setup_github_workspace(worker, workspace)
        elif self.process == JobProcess.BITBUCKET:
            self.setup_bitbucket_workspace(worker, workspace)
        elif self.process == JobProcess.GITLAB:
            self.setup_gitlab_workspace(worker, workspace)
        else:
            pass  # TODO: Have to raise an error here.

        # The workspace should be all configured correctly now.
        worker.change_directory(workspace)

        # Have the worker load the module.
        self.setup_module(worker)

    def run_install(self, worker):
        pass

    def run_script(self, worker):
        pass

    def run_after_complete(self, worker):
        pass

    def run_after_success(self, worker):
        pass

    def run_after_failure(self, worker):
        pass

    def setup_module(self, worker):
        pass

    def setup_archive_workspace(self, worker, workspace):
        path = worker.pathlib

        # Make space for the archive to be created.
        archive = path.join(worker.tmp, 'archive')
        if worker.is_file(archive):
            worker.remove_file(archive)

        status = worker.download_file(self.params['url'], archive)
        # TODO: Check status here and error if not correct.

        # Try to extract the archive first as a .tar file.
        success = False
        try:
            with tarfile.TarFile(archive, mode='r') as f:
                f.extractall(workspace)
            success = True
        except Exception:
            pass

        # If .tar is not successful, try as a .zip file.
        if not success:
            try:
                with zipfile.ZipFile(archive) as f:
                    f.extractall(workspace)
                success = True
            except Exception:
                pass

        # We couldn't extract the archive, time to error out.
        if not success:
            raise Exception()  # TODO: Need a more descriptive exception.

        # Delete the archive file to free up disk space.
        if worker.is_file(archive):
            worker.remove_file(archive)

    def setup_github_workspace(self, worker, workspace):
        pass  # TODO: Implement this.

    def setup_bitbucket_workspace(self, worker, workspace):
        pass  # TODO: Implement this.

    def setup_gitlab_workspace(self, worker, workspace):
        pass  # TODO: Implement this.
