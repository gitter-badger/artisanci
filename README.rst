Artisan CI
==========

.. image:: https://img.shields.io/travis/SethMichaelLarson/artisan-ci/master.svg
    :target: https://travis-ci.org/SethMichaelLarson/artisan-ci
    :alt: Linux and MacOS Build Status
.. image:: https://img.shields.io/appveyor/ci/SethMichaelLarson/artisan-ci/master.svg
    :target: https://ci.appveyor.com/project/SethMichaelLarson/artisan-ci
    :alt: Windows Build Status
.. image:: https://img.shields.io/codecov/c/github/SethMichaelLarson/artisan-ci/master.svg
    :target: https://codecov.io/gh/SethMichaelLarson/artisan-ci
    :alt: Code Coverage
.. image:: https://img.shields.io/codeclimate/github/SethMichaelLarson/artisan-ci.svg
    :target: https://codeclimate.com/github/SethMichaelLarson/artisan-ci
    :alt: Code Health
.. image:: https://readthedocs.org/projects/artisan-ci/badge/?version=latest
    :target: http://artisan-ci.readthedocs.io
    :alt: Documentation Build Status
.. image:: https://pyup.io/repos/github/sethmichaellarson/artisan-ci/shield.svg
     :target: https://pyup.io/repos/github/sethmichaellarson/artisan-ci
     :alt: Dependency Versions
.. image:: https://img.shields.io/pypi/v/artisan.svg
    :target: https://pypi.python.org/pypi/artisan
    :alt: PyPI Version
.. image:: https://img.shields.io/badge/say-thanks-ff69b4.svg
    :target: https://saythanks.io/to/SethMichaelLarson
    :alt: Say Thanks to the Maintainers
.. image:: https://img.shields.io/twitter/follow/artisan_ci.svg?style=social&label=Follow
    :target: https://twitter.com/artisan_ci
    :alt: Follow Artisan CI on Twitter

Community powered Continuous Integration! :beers: Run your own CI service out of
the box and donate cycles to your favorite projects and developers.

**WARNING: This project is very young and not nearly complete. Many many things can change. Do NOT use yet.**

Features
--------

- Continuous Integration builders in a box. Run your own private farm.
- Integrates with GitHub, GitLab, and BitBucket for automated builds and testing.
- Support for all major platforms (Linux, Windows, Mac OS, and Solaris).
- Support for virtualized builders via `VirtualBox <https://www.virtualbox.org>`_.
- Interface for providing your own builders to other projects.
- Provides an extensible module interface for customized use-cases.

Supported Platforms
-------------------

Artisan CI supports the following Python versions:

- CPython 2.7, 3.3+
- PyPy 5.3.1+

We do not yet support PyPy3 as it's still on Python 3.2.5. This will change when PyPy3 supports 3.3+

Artisan CI supports the following four platforms as capable of running a builder farm:

- Windows Vista SP1+
- Mac OSX 10.9+
- Linux 2.4+ (Debian 7+, Ubuntu 12.04+, Oracle 5+. RedHat 5+, Fedora 6+, Gentoo, openSUSE 11.4+)
- Solaris 10, 11

Virtualized builders support a very large range of guest platforms
(Copied from `VirtualBox website <https://www.virtualbox.org/manual/ch03.html#guestossupport>`_):

- Windows NT 4.0
- Windows 2000, XP, Vista, 7, 8, 8.1, 10
- Windows Server 2003, 2008, 2012
- DOS / Windows 3.x / 95 / 98 / ME
- Linux 2.6, 3.x (Limited support for Linux 2.4<)
- Solaris 10 (u6 and higher), Solaris 11, Express
- OS/2 Warp 4.5 (Limited support)
- Mac OSX (`See limitations of Mac OSX guests <https://www.virtualbox.org/manual/ch03.html#guestossupport>`_)

Although VirtualBox supports NetBSD and OpenBSD it does not support Guest Additions
for those platforms. Artisan CI requires Guest Additions to operate currently. This
may change in the future.

Getting Started
---------------

There are many guides on how to get started hosting your own builders or
setting up a project to use other builders. Guides are written for each platform
that Artisan CI supports.

The guides also feature many examples on how best to configure a farm. If you're
having trouble getting Artisan CI working correctly do not hesitate to `open an
issue on GitHub <https://github.com/SethMichaelLarson/artisan-ci/issues>`_.

References
----------

The `Module and API Reference on readthedocs.io <http://artisan-ci.readthedocs.io>`_
provides documentation for the web API and the module ``artisan``.

Issues and Support
------------------

All support requests and issue reports should be
`filed on GitHub as an issue <https://github.com/SethMichaelLarson/artisan-ci/issues>`_.
Make sure to follow the template so your request may be as handled as quickly as possible.

Contributing
------------

We welcome community contributions, please see `our guide for Contributors <http://artisan-ci.readthedocs.io/en/latest/contributing.html>`_ for the best places to start and help.

License
-------

Artisan CI is made available under the Apache 2.0 License. For more details, see `LICENSE.txt <https://github.com/SethMichaelLarson/artisan-ci/blob/master/LICENSE.txt>`_.
