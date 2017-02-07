Changelog
=========

Release 0.0.0 (Development)
---------------------------

* Added :class:`artisan.LocalWorker`.
* Added :class:`artisan.SshWorker`.
* Added faster path support for :class:`artisan.SshWorker`.
* Added :py:attr:`artisan.BaseWorker.platform`, :py:attr:`artisan.BaseWorker.hostname`,
  and :py:attr:`artisan.BaseWorker.home` to :class:`artisan.BaseWorker`.
* Added :py:attr:`artisan.BaseCommand.stdin` to :class:`artisan.BaseCommand`.
* Added :meth:`artisan.BaseWorker.change_file_mode`, :meth:`artisan.BaseWorker.change_file_owner`
  and :meth:`artisan.BaseWorker.change_file_group`. (`PR #55 <https://github.com/SethMichaelLarson/artisan/pull/55>`_)
* Fixed support for ``follow_symlinks`` in :meth:`artisan.BaseWorker.change_file_owner`,
  :meth:`artisan.BaseWorker.change_file_group, and :meth:`artisan.BaseWorker.change_file_mode`.
  (`PR #58 <https://github.com/SethMichaelLarson/artisan/pull/58>`_)
* Added support for exclusive file opening via ``open_file(path, mode='x')`` for BaseWorker. (`PR #71 <https://github.com/SethMichaelLarson/artisan/pull/71>`_)
* Added support for ``get_cpu_usage()``, ``get_cpu_count()``, ``get_memory_usage()``,
  ``get_swap_usage()``, ``get_disk_usage()``, and ``get_disk_partitions()`` to BaseWorker.
  (`PR #74 <https://github.com/SethMichaelLarson/artisan/pull/74>`_)