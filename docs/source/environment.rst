Environment Variables
=====================

All Builds
----------

These environment variables are used in every build on Artisan CI.
They should always be defined and available with these values:

- ``ARTISAN=true``
- ``ARTISAN_VERSION``: Current version of Artisan CI being used.
- ``CI=true``
- ``CONTINUOUS_INTEGRATION=true``

Additionally the following environment variables are used and set to different
values depending on the configuration of the build.

- ``ARTISAN_ALLOW_FAILURE``: ``true`` if the build is allowed to fail, ``false`` otherwise.
- ``ARTISAN_BUILD_DIR``: Set to be the directory where the job is being built.
- ``ARTISAN_BUILD_ID``: Unique ID for the build in the form of a UUID.
- ``ARTISAN_BUILD_TRIGGER`` One of ``github``, ``gitlab``, ``bitbucket`` or ``manual``.
- ``ARTISAN_BUILD_TYPE``: Can be either ``local`` for a local build or ``git``/``mercurial`` for a triggered build.
- ``ARTISAN_USERNAME``: Name of the user that triggered the build. This can either be a GitHub, GitLab, BitBucket, or local username.

Git Builds
----------

Builds that have a ``ARTISAN_BUILD_TYPE`` equal to ``git`` are triggered
from GitHub or GitLab. These builds will have the following environment
variables defined in addition to the above variables:

- ``ARTISAN_GIT_BRANCH``
- ``ARTISAN_GIT_COMMIT``
- ``ARTISAN_GIT_REPOSITORY``
- ``ARTISAN_GIT_TAG``

Mercurial Builds
----------------

Builds that have a ``ARTISAN_BUILD_TYPE`` equal to ``mercurial`` are triggered
from BitBucket. These builds will have the following environment variables
defined in a addition to the above variables:

- ``ARTISAN_MERCURIAL_BRANCH``
- ``ARTISAN_MERCURIAL_REPOSITORY``
