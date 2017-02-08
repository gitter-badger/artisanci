Changelog
=========

Under Development
-----------------

* Added :class:`artisan.worker.LocalWorker`.
* Added :class:`artisan.worker.SshWorker`.
* Added faster path support for :class:`artisan.worker.SshWorker`.
* Added :py:attr:`artisan.worker.BaseWorker.platform`, :py:attr:`artisan.worker.BaseWorker.hostname`,
  and :py:attr:`artisan.worker.BaseWorker.home` to :class:`artisan.worker.BaseWorker`.
* Added :py:attr:`artisan.worker.BaseCommand.stdin` to :class:`artisan.worker.BaseCommand`.
* Added :meth:`artisan.worker.BaseWorker.change_file_mode`, :meth:`artisan.worker.BaseWorker.change_file_owner`
  and :meth:`artisan.worker.BaseWorker.change_file_group`. (`PR #55 <https://github.com/SethMichaelLarson/artisan/pull/55>`_)
* Fixed support for ``follow_symlinks`` in :meth:`artisan.worker.BaseWorker.change_file_owner`,
  :meth:`artisan.worker.BaseWorker.change_file_group, and :meth:`artisan.BaseWorker.change_file_mode`.
  (`PR #58 <https://github.com/SethMichaelLarson/artisan/pull/58>`_)
* Added support for exclusive file opening via ``open_file(path, mode='x')`` for :class:`artisan.worker.BaseWorker`. (`PR #71 <https://github.com/SethMichaelLarson/artisan/pull/71>`_)
* Added support for :meth:`artisan.worker.BaseWorker.get_cpu_usage()`,
  :meth:`artisan.worker.BaseWorker.get_cpu_count()`, :meth:`artisan.worker.BaseWorker.get_memory_usage()`,
  :meth:`artisan.worker.BaseWorker.get_swap_usage()`, :meth:`artisan.worker.BaseWorker.get_disk_usage()`,
  and :meth:`artisan.worker.BaseWorker.get_disk_partitions()` to :class:`artisan.worker.BaseWorker`.
  (`PR #74 <https://github.com/SethMichaelLarson/artisan/pull/74>`_)