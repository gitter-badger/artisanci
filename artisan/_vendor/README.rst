Vendored Modules
================

If you are planning to submit a Pull Request against any of the libraries in the
``vendor/`` directory than do not go any further. These are independent libraries
which are vendored into Artisan. Any changes to these libraries should be made in
their respective upstream repository and then will be propagated here.

The exception to the above rule is ``pyvbox``, see below for explanation.

pyvbox 1.0.0
------------
License: MIT

It appears that ``pyvbox`` is not currently maintained. Last release was a year ago.
All changes *should* be submitted against the `GitHub project <https://github.com/mjdorma/pyvbox>`_
but it seems that there is slim chance of getting a new release. Feel free to submit
any changes to Artisan CI in addition to the actual GitHub project.

vboxapi Revision 109501
-----------------------
License: CDDL-1.0

From the VirtualBox SDK kit which can be found on the
`VirtualBox Downloads page <https://www.virtualbox.org/wiki/Downloads>`_
available for any host. All changes should be submitted upstream.
The module ``vboxapi`` is licensed under CDDL-1.0 as long as the code is
distributed without any modifications. All source code within
``artisan/_vendor/vboxapi/...`` is not changed from it's distributed form.
