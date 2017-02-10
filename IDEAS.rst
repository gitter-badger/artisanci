Ideas
=====

This is simply a place for me to log down my ideas.

Artisan Run Modes
-----------------

- ``local``
  Would load in ``.artisan.yml`` for the project and execute only the jobs that
  were possible to run locally. If there is a farm registered to your token then
  attempt to use that farm as well as long as connectivity to ``artisan.io`` is
  possible

- ``global``
  Loads ``.artisan.yml`` and runs each job on the global farm if it cannot be