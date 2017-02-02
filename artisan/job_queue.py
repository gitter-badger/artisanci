""" Implementation of a JobQueue that schedules jobs
to a group of workers that are registered to the queue. """
import threading

__all__ = [
    'JobQueue'
]


class JobQueue(object):
    def __init__(self):
        self._lock = threading.RLock()
        self._idle_jobs = []
        self._busy_jobs = []
        self._idle_workers = []
        self._busy_workers = []
        self._queue_paused = False
        self._queue_updated = False
        self._queue_idle = threading.Event()

        self._update_queue()

    @property
    def is_idle(self):
        return self._queue_idle.is_set()

    def pause_queue(self):
        """ Pauses the JobQueue from processing any
        new jobs. Jobs that are already executing will
        finish up as normal. """
        with self._lock:
            if self._queue_paused:
                raise ValueError('JobQueue is already paused.')
            self._queue_paused = True
            self._queue_updated = False

    def resume_queue(self):
        """ Resumes the queue by allowing new jobs to
        be scheduled by workers. """
        with self._lock:
            if not self._queue_paused:
                raise ValueError('JobQueue is not paused.')
            self._queue_paused = False
            if self._queue_updated:
                self._queue_updated = False
                self._update_queue()

    def wait(self, timeout=None):
        """ Wait for the queue to be idle. """
        self._queue_idle.wait(timeout)

    def add_job(self, job):
        with self._lock:
            if job in self._idle_jobs + self._busy_jobs:
                raise ValueError('Job is already in the queue.')
            self._idle_jobs.append(job)
            self._update_queue()

    def remove_job(self, job):
        with self._lock:
            if job not in self._idle_jobs:
                raise ValueError('Job is not in the queue.')
            self._idle_jobs.remove(job)

    def add_worker(self, worker):
        with self._lock:
            if worker in self._idle_workers + self._busy_workers:
                raise ValueError('Worker is already working the queue.')
            self._idle_workers.append(worker)
            self._update_queue()

    def _update_queue(self):
        with self._lock:
            if self._queue_paused:
                self._queue_updated = True
            else:
                while len(self._idle_jobs) > 0 and len(self._idle_workers) > 0:
                    worker = self._idle_workers[0]
                    job = self._idle_jobs[0]
                    job.add_callback(self._job_callback, worker)
                    job.worker = worker
                    job.start()

                    del self._idle_workers[0]
                    del self._idle_jobs[0]

                    self._busy_jobs.append(job)
                    self._busy_workers.append(worker)

                if self._queue_idle.is_set():
                    if len(self._busy_workers) > 0:
                        self._queue_idle.clear()
                elif len(self._busy_workers) == 0:
                    self._queue_idle.set()

    def _job_callback(self, job, worker):
        with self._lock:
            self._busy_jobs.remove(job)
            self._busy_workers.remove(worker)
            self._idle_workers.append(worker)
        self._update_queue()
