import os
import uuid

__all__ = [
    'Job',
    'LocalJob',
    'GitJob'
]


class Job(object):
    def __init__(self, script, params):
        self.script = script
        self.params = params

        self._cleanup_calls = []

    def setup(self, worker):
        raise NotImplementedError()

    def add_cleanup(self, func, *args, **kwargs):
        self._cleanup_calls.append((func, args, kwargs))

    def cleanup(self):
        for func, args, kwargs in self._cleanup_calls:
            try:
                func(*args, **kwargs)
            except Exception:
                pass


class LocalJob(Job):
    def __init__(self, script, path):
        super(LocalJob, self).__init__(script, {'path': path})

    def setup(self, worker):
        pass


class GitJob(Job):
    def __init__(self, script, repo, branch):
        super(GitJob, self).__init__(script, {'repo': repo,
                                              'branch': branch})

    def setup(self, worker):
        repo = self.params['repo']
        if repo.endswith('.git'):
            repo = repo[:-4]
        worker.change_directory(worker.tmp)
        tmp_dir = uuid.uuid4().hex
        worker.create_directory(tmp_dir)
        worker.change_directory(tmp_dir)
        worker.execute('git clone --depth=50 %s' % self.params['repo'])
        self.add_cleanup(worker.remove_directory, os.path.join(tmp_dir, os.path.basename(repo)))
        worker.change_directory(os.path.basename(repo))
        worker.execute('git fetch origin %s' % self.params['branch'])
        worker.execute('git checkout -qf FETCH_HEAD')

