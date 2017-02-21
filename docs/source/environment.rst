Environment Variables
=====================

General
-------

These environment variables are used in every build on Artisan CI.
They should always be defined and available with these values:

- ``CI=true``
- ``ARTISAN=true``
- ``CONTINUOUS_INTEGRATION=true``

Additionally the following environment variables are used and set to different
values depending on the configuration of the build.

- ``ARTISAN_ALLOW_FAILURE``: ``true`` if the build is allowed to fail, ``false`` otherwise.
- ``ARTISAN_BUILD_DIR``: Set to be the directory where the job is being built.
- ``ARTISAN_BUILD_ID``: UUID for the id of the build.
- ``ARTISAN_BUILD_TYPE``: Can be either ``local`` for a local build or ``git`` for a build using git.
- ``ARTISAN_OS_PLATFORM``: Name of the platform that the build is running on.

Git Builds
----------

Builds that have a ``ARTISAN_BUILD_TYPE`` equal to ``git`` will have the following
environment variables also defined:

- ``ARTISAN_