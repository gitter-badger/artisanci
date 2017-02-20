import os
import sys
import uuid
from .worker import Worker

__all__ = [
    'Job',
    'LocalJob',
    'GitJob'
]


class Job(object):
    def __init__(self, script, params, report):
        self.script = script
        self.params = params
        self.report = report

        self._cleanup_calls = []

    def setup(self, worker):
        assert isinstance(worker, Worker)
        worker.add_listener(self.report)

    def execute(self, worker):

        # Importing the script module.
        script_path = self.script
        if os.path.isabs(self.script):
            script_path = os.path.join(worker.cwd, script_path)
        script_module = os.path.basename(script_path)
        if script_module.endswith('.py'):
            script_module = script_module[:-3]
        sys.path.insert(0, os.path.dirname(script_path))
        script = __import__(script_module)
        sys.path = sys.path[1:]

        # TODO: Here

    def add_cleanup(self, func, *args, **kwargs):
        self._cleanup_calls.append((func, args, kwargs))

    def cleanup(self, worker):
        worker.remove_listener(self.report)
        for func, args, kwargs in self._cleanup_calls:
            try:
                func(*args, **kwargs)
            except Exception:
                pass

    def make_temporary_directory(self, worker):
        assert isinstance(worker, Worker)
        worker.change_directory(worker.tmp)
        tmp_dir = uuid.uuid4().hex
        while not worker.is_directory(tmp_dir):
            tmp_dir = uuid.uuid4().hex
        worker.create_directory(tmp_dir)
        worker.change_directory(tmp_dir)
        self.add_cleanup(worker.remove_directory, tmp_dir)
        return tmp_dir


class LocalJob(Job):
    def __init__(self, script, path, report):
        super(LocalJob, self).__init__(script, {'path': path}, report)


class GitJob(Job):
    def __init__(self, script, repo, branch, report):
        params = {'repo': repo,
                  'branch': branch}
        super(GitJob, self).__init__(script, params, report)

    def setup(self, worker):
        super(GitJob, self).setup(worker)
        repo = self.params['repo']
        if repo.endswith('.git'):
            repo = repo[:-4]
        tmp_dir = self.make_temporary_directory(worker)
        worker.execute('git clone --depth=50 %s' % self.params['repo'])
        repository = os.path.join(tmp_dir, worker.list_directory(tmp_dir)[0])
        worker.change_directory(repository)
        worker.execute('git fetch origin %s' % self.params['branch'])
        worker.execute('git checkout -qf FETCH_HEAD')
