Artisan
=======

.. image:: https://img.shields.io/travis/artisanci/artisan/master.svg
    :target: https://travis-ci.org/artisanci/artisan
    :alt: Linux and MacOS Build Status
.. image:: https://img.shields.io/appveyor/ci/artisanci/artisan/master.svg
    :target: https://ci.appveyor.com/project/artisanci/artisan
    :alt: Windows Build Status
.. image:: https://img.shields.io/codecov/c/github/artisanci/artisan/master.svg
    :target: https://codecov.io/gh/artisanci/artisan
    :alt: Test Suite Coverage
.. image:: https://img.shields.io/codeclimate/github/artisanci/artisan.svg
    :target: https://codeclimate.com/github/artisanci/artisan
    :alt: Code Health
.. image:: https://readthedocs.org/projects/artisan/badge/?version=latest
    :target: http://artisan.readthedocs.io
    :alt: Documentation Build Status
.. image:: https://pyup.io/repos/github/artisanci/artisan/shield.svg
     :target: https://pyup.io/repos/github/artisanci/artisan
     :alt: Dependency Versions
.. image:: https://img.shields.io/pypi/v/artisan.svg
    :target: https://pypi.python.org/pypi/artisan
    :alt: PyPI Version
.. image:: https://img.shields.io/badge/say-thanks-ff69b4.svg
    :target: https://saythanks.io/to/SethMichaelLarson
    :alt: Say Thanks to the Maintainers

Modern, flexible, and platform-agnostic interface for automation, continuous integration, and farm management.

Features and Support
--------------------

- Artisan is a full-featured self-hosted Continuous Integration service that integrates
  with popular source code management services.
- Supports GitHub, BitBucket, and GitLab

Getting Started with Artisan
----------------------------

Artisan is available on PyPI can be installed with `pip <https://pip.pypa.io>`_.::

    $ python -m pip install artisan

To install the latest development version from `Github <https://github.com/artisanci/artisan>`_::

    $ python -m pip install git+git://github.com/SethMichaelLarson/artisan.git


If your current Python installation doesn't have pip available, try `get-pip.py <bootstrap.pypa.io>`_

After installing Artisan, head to artisan.io and register and create an API key
for free with a GitHub account.

If you're planning on using Artisan for only personal use then setup is easy.

.. code-block:: python

    import artisan

    farm = artisan.Farm()
    farm


API Reference
-------------

The `API Reference on readthedocs.io <http://artisan.readthedocs.io>`_ provides API-level documentation.

Support / Report Issues
-----------------------

All support requests and issue reports should be
`filed on Github as an issue <https://github.com/SethMichaelLarson/artisan/issues>`_.
Make sure to follow the template so your request may be as handled as quickly as possible.
Please respect contributors by not using personal contacts for support requests.

Contributing
------------

We welcome community contributions, please see `our guide for Contributors <http://artisan.readthedocs.io/en/latest/contributing.html>`_ for the best places to start and help.

License
-------

Artisan is made available under the Apache 2.0 License. For more details, see `LICENSE.txt <https://github.com/artisanci/artisan/blob/master/LICENSE.txt>`_.

Sponsorship
-----------

If your company benefits from this library please consider sponsoring its development.
Money earned from sponsoring goes primarily towards maintaining hosts and infrastructure.
