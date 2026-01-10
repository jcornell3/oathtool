.. image:: https://img.shields.io/pypi/v/oathtool.svg
   :target: https://pypi.org/project/oathtool

.. image:: https://img.shields.io/pypi/pyversions/oathtool.svg

.. image:: https://github.com/jaraco/oathtool/actions/workflows/main.yml/badge.svg
   :target: https://github.com/jaraco/oathtool/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. .. image:: https://readthedocs.org/projects/PROJECT_RTD/badge/?version=latest
..    :target: https://PROJECT_RTD.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2025-informational
   :target: https://blog.jaraco.com/skeleton

TOTP code generator based on oathtool.

Usage
=====

Command-line::

    $ python -m oathtool $key

API::

    >>> oathtool.generate_otp(key)

Create standalone script (Unix)::

    $ python -m oathtool.generate-script
    $ ./oathtool $key

Don't want to install oathtool, but just want the script? Use
`pip-run <https://pypi.org/project/pip-run>`_::

    $ pip-run oathtool -- -m oathtool.generate-script
    $ ./oathtool $key


``generate-script`` also takes an arbitrary target path in
case you wish to generate the script elsewhere::

    $ python -m oathtool.generate-script ~/bin/my-oathtool

Or install with `pipx <https://pipxproject.github.io/pipx/>`_::

    $ pipx install oathtool
    $ oathtool $key

Windows Executable and MSIX Package
====================================

For Windows users, oathtool is available as a standalone executable and MSIX package.

Standalone Windows Executable
------------------------------

A standalone Windows executable (``oathtool.exe``) is built using PyInstaller.
This executable requires no Python installation.

To build the executable::

    pip install pyinstaller
    pyinstaller oathtool.spec

The executable will be created at ``dist\oathtool.exe``.

Usage::

    oathtool.exe $key

MSIX Package Installation
--------------------------

For streamlined installation on Windows 10/11, MSIX packages are available
from GitHub releases for tagged versions.

Download and install:

1. Download the ``.msix`` file from the `GitHub Releases page <https://github.com/jaraco/oathtool/releases>`_
2. Double-click the ``.msix`` file to install
3. (Developer Mode required for unsigned packages)

Or install via PowerShell::

    Add-AppxPackage -Path oathtool-x.y.z.msix

Building MSIX Package
---------------------

To build the MSIX package locally::

    # First build the executable
    pyinstaller oathtool.spec

    # Then build the MSIX package
    .\build-msix.ps1 -Version "1.2.3"

The MSIX package will be created at ``dist\oathtool-1.2.3.msix``.

**Note:** Building MSIX packages requires the Windows SDK (includes MakeAppx.exe).

For detailed information on MSIX packaging, see ``msix/README.md``.
