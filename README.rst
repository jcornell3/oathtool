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

Google/Microsoft Authenticator Replacement
===========================================

This tool generates the same 6-digit TOTP codes as Google Authenticator,
Microsoft Authenticator, and other 2FA apps. Perfect for:

- Generating codes from the command line
- Automating 2FA in scripts
- Backing up your 2FA without a phone
- Using 2FA on Windows without mobile apps

Getting Your Secret Key
------------------------

When setting up 2FA on websites, you'll see a QR code. To use oathtool:

1. Look for "Can't scan QR code?" or "Enter this text code instead" link
2. Copy the secret key (usually 16-32 characters, Base32 format)
3. Examples of valid keys:

   - ``JBSWY3DPEHPK3PXP``
   - ``GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ``
   - ``MZXW 6YTB OJUW U23M NU`` (spaces are automatically removed)

**Common Services:**

- **Google:** https://myaccount.google.com/security → 2-Step Verification
- **Microsoft:** https://account.microsoft.com/security → Security info
- **GitHub:** Settings → Password and authentication → Two-factor authentication
- **AWS:** IAM → Users → Security credentials → MFA

Quick Start Examples
--------------------

**Command-line (cross-platform)**::

    # Generate a code
    python -m oathtool JBSWY3DPEHPK3PXP

    # With pipx
    oathtool JBSWY3DPEHPK3PXP

    # From stdin (secure - key not in process list)
    echo JBSWY3DPEHPK3PXP | oathtool

**Python API**::

    import oathtool

    # Generate current TOTP code
    code = oathtool.generate_otp('JBSWY3DPEHPK3PXP')
    print(f"Your code: {code}")

    # Use in login automation
    secret = 'JBSWY3DPEHPK3PXP'
    totp_code = oathtool.generate_otp(secret)
    # Now use totp_code in your login flow

Windows Usage Examples
======================

Using the Standalone Executable
---------------------------------

Download ``oathtool.exe`` from GitHub Releases and use directly::

    # Basic usage
    oathtool.exe JBSWY3DPEHPK3PXP

    # From PowerShell
    PS> .\oathtool.exe JBSWY3DPEHPK3PXP
    123456

    # From Command Prompt
    C:\> oathtool.exe JBSWY3DPEHPK3PXP
    123456

    # Pipe input (secure)
    PS> "JBSWY3DPEHPK3PXP" | .\oathtool.exe
    123456

**PowerShell Script Example**::

    # save-totp.ps1 - Generate TOTP code
    param([string]$Service = "google")

    $secrets = @{
        google = "JBSWY3DPEHPK3PXP"
        github = "MZXW6YTBOJUWU23MNU"
        aws    = "GEZDGNBVGY3TQOJQ"
    }

    $code = & .\oathtool.exe $secrets[$Service]
    Write-Host "$Service code: $code"

    # Copy to clipboard
    Set-Clipboard $code
    Write-Host "Code copied to clipboard!"

Usage::

    PS> .\save-totp.ps1 -Service google
    google code: 123456
    Code copied to clipboard!

**Batch File Example**::

    @echo off
    REM get-code.bat - Quick TOTP code generator

    set GOOGLE_KEY=JBSWY3DPEHPK3PXP
    set GITHUB_KEY=MZXW6YTBOJUWU23MNU

    echo Google Code:
    oathtool.exe %GOOGLE_KEY%

    echo.
    echo GitHub Code:
    oathtool.exe %GITHUB_KEY%

    pause

**Secure Key Storage (PowerShell)**::

    # Store encrypted secrets
    $secret = "JBSWY3DPEHPK3PXP"
    $secure = ConvertTo-SecureString $secret -AsPlainText -Force
    $encrypted = $secure | ConvertFrom-SecureString
    $encrypted | Out-File "google-2fa.txt"

    # Retrieve and use
    $encrypted = Get-Content "google-2fa.txt"
    $secure = $encrypted | ConvertTo-SecureString
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $secret = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    $code = & .\oathtool.exe $secret
    Write-Host "Code: $code"

Using with Python on Windows
-----------------------------

**Install via pip**::

    # Install Python from python.org or Microsoft Store
    pip install oathtool

**Simple Python script** (``get_totp.py``)::

    import oathtool
    import sys

    # Dictionary of your 2FA secrets
    SECRETS = {
        'google': 'JBSWY3DPEHPK3PXP',
        'github': 'MZXW6YTBOJUWU23MNU',
        'microsoft': 'GEZDGNBVGY3TQOJQ',
    }

    def get_code(service):
        """Generate TOTP code for a service."""
        if service not in SECRETS:
            print(f"Unknown service: {service}")
            print(f"Available: {', '.join(SECRETS.keys())}")
            return None

        code = oathtool.generate_otp(SECRETS[service])
        return code

    if __name__ == '__main__':
        if len(sys.argv) != 2:
            print("Usage: python get_totp.py <service>")
            print(f"Available services: {', '.join(SECRETS.keys())}")
            sys.exit(1)

        service = sys.argv[1].lower()
        code = get_code(service)
        if code:
            print(f"{service}: {code}")

Usage::

    C:\> python get_totp.py google
    google: 123456

    C:\> python get_totp.py github
    github: 789012

**GUI Application Example** (using tkinter)::

    import oathtool
    import tkinter as tk
    from tkinter import ttk
    import time

    class TOTPGenerator:
        def __init__(self, root):
            self.root = root
            root.title("TOTP Code Generator")

            self.secrets = {
                'Google': 'JBSWY3DPEHPK3PXP',
                'GitHub': 'MZXW6YTBOJUWU23MNU',
                'Microsoft': 'GEZDGNBVGY3TQOJQ',
            }

            # Service selector
            ttk.Label(root, text="Service:").grid(row=0, column=0, padx=5, pady=5)
            self.service_var = tk.StringVar()
            service_combo = ttk.Combobox(root, textvariable=self.service_var,
                                        values=list(self.secrets.keys()), state='readonly')
            service_combo.grid(row=0, column=1, padx=5, pady=5)
            service_combo.current(0)

            # Generate button
            ttk.Button(root, text="Generate Code", command=self.generate).grid(row=1, column=0, columnspan=2, pady=10)

            # Code display
            self.code_label = ttk.Label(root, text="------", font=('Courier', 24, 'bold'))
            self.code_label.grid(row=2, column=0, columnspan=2, pady=10)

            # Copy button
            ttk.Button(root, text="Copy to Clipboard", command=self.copy).grid(row=3, column=0, columnspan=2)

            self.current_code = None

        def generate(self):
            service = self.service_var.get()
            secret = self.secrets[service]
            self.current_code = oathtool.generate_otp(secret)
            self.code_label.config(text=self.current_code)

        def copy(self):
            if self.current_code:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.current_code)
                self.root.update()

    if __name__ == '__main__':
        root = tk.Tk()
        app = TOTPGenerator(root)
        root.mainloop()

Save as ``totp_gui.py`` and run::

    python totp_gui.py

Common Automation Scenarios
----------------------------

**Auto-login Script (PowerShell)**::

    # auto-login.ps1
    param([string]$Username, [string]$Password, [string]$Secret)

    # Generate TOTP code
    $totp = & .\oathtool.exe $Secret

    # Use with Selenium or other automation
    # Example: Fill in login form
    Write-Host "Logging in as $Username"
    Write-Host "TOTP Code: $totp"
    # ... add your automation code here

**Backup All Codes (PowerShell)**::

    # backup-codes.ps1 - Generate all codes at once
    $secrets = @{
        "Google"    = "JBSWY3DPEHPK3PXP"
        "GitHub"    = "MZXW6YTBOJUWU23MNU"
        "Microsoft" = "GEZDGNBVGY3TQOJQ"
        "AWS"       = "GEZDGNBVGY3TQOJR"
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "=== TOTP Codes Generated: $timestamp ===`n"

    foreach ($service in $secrets.Keys | Sort-Object) {
        $code = & .\oathtool.exe $secrets[$service]
        Write-Host ("{0,-15} {1}" -f $service, $code)
    }

Output::

    === TOTP Codes Generated: 2026-01-09 15:30:00 ===

    AWS             123456
    GitHub          789012
    Google          345678
    Microsoft       901234

**Scheduled Task (Generate codes every 30 seconds)**::

    # watch-codes.ps1 - Auto-refresh codes
    while ($true) {
        Clear-Host
        Write-Host "=== Current TOTP Codes ===" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to exit`n"

        & .\backup-codes.ps1

        Write-Host "`nRefreshing in 30 seconds..."
        Start-Sleep -Seconds 30
    }

Security Best Practices
-----------------------

**DO:**

- ✅ Store secrets in encrypted files (see PowerShell example above)
- ✅ Use stdin to pass keys (not command-line arguments)
- ✅ Keep backup codes from services in a secure location
- ✅ Use Windows Credential Manager for secret storage

**DON'T:**

- ❌ Hardcode secrets in scripts in shared repositories
- ❌ Pass secrets as command-line arguments in production
- ❌ Store secrets in plain text files
- ❌ Share secrets via email or chat

**Secure Key Storage with Windows Credential Manager**::

    # Store secret
    PS> cmdkey /generic:oathtool-google /user:secret /pass:JBSWY3DPEHPK3PXP

    # Retrieve secret (requires script)
    # See: https://docs.microsoft.com/en-us/windows/security/identity-protection/credential-guard/

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

**⚠️ Important: Unsigned Package**

The MSIX packages distributed via GitHub releases are **unsigned** (no trusted certificate).
Before installation, you must sign the package yourself using the provided script.

**Installation Steps:**

1. Download both files from GitHub:

   - The ``.msix`` package from `GitHub Releases <https://github.com/jcornell3/oathtool/releases>`_
   - The ``FIX-MSIX-INSTALL.ps1`` script from the `repository <https://github.com/jcornell3/oathtool>`_

2. Place both files in the same directory

3. **Right-click** ``FIX-MSIX-INSTALL.ps1`` and select **"Run as Administrator"**

4. The script will:

   - Create a self-signed certificate (CN=TestPublisher)
   - Install it to Trusted Root Certification Authorities
   - Sign the MSIX package
   - Display installation instructions

5. Double-click the signed MSIX file to install

6. Click **Install** when prompted

**⚠️ Requires Administrator privileges** because the script installs a certificate to the
system-wide Trusted Root store.

**Note:** Developer Mode is **not** required or used. The signed package will install
on any Windows 10/11 system once signed.

**Step 3: Install the Package**

Download and install:

1. Download the ``.msix`` file from the `GitHub Releases page <https://github.com/jcornell3/oathtool/releases>`_
2. Double-click the ``.msix`` file to install
3. Click **Install** when prompted
4. The app will appear in your Start Menu

Or install via PowerShell::

    Add-AppxPackage -Path oathtool-x.y.z.msix

**Alternative: Use Portable Executable**

If you can't enable Developer Mode, use the standalone ``oathtool.exe`` instead -
no installation required! Download from GitHub Releases.

**Note:** Developer Mode is only needed for installation. You can disable it
afterward and the app will continue to work.

**For detailed installation instructions, troubleshooting, and signing options,
see:** ``INSTALLING_UNSIGNED_MSIX.md``

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
