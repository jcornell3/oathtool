# MSIX Distribution Strategy

This document explains how the oathtool MSIX packages are built and distributed.

## Overview

The MSIX packages distributed via GitHub Releases are **unsigned** by design. This is the standard approach for open-source Windows applications that don't have a paid code signing certificate.

## Build Process

### Local Development

When building locally for testing:

```powershell
# Build unsigned package (default)
.\build-msix.ps1 -Version "1.2.3"

# Build and sign (requires certificate)
.\build-msix.ps1 -Version "1.2.3" -Sign
```

The `-Sign` parameter is optional and only works if you have a valid code signing certificate installed.

### GitHub Actions (Production Releases)

The GitHub Actions workflow (`.github/workflows/main.yml`) automatically builds MSIX packages for tagged releases:

1. **Triggered by:** Pushing a git tag (e.g., `v1.2.3`)
2. **Runs on:** Windows runner with Windows SDK pre-installed
3. **Build command:** `.\build-msix.ps1 -Version "1.2.3"` (no `-Sign` parameter)
4. **Result:** Unsigned MSIX package
5. **Distribution:** Automatically attached to GitHub Release

**The packages uploaded to GitHub Releases are UNSIGNED.**

## Installation for End Users

End users who download the MSIX package from GitHub Releases have **two options**:

### Option 1: Enable Developer Mode (Recommended)

**Easiest for most users.**

1. Open Windows Settings
2. Enable Developer Mode:
   - **Windows 11:** System → For developers (or System → Advanced)
   - **Windows 10:** Update & Security → For developers
3. Download and double-click the MSIX package
4. Click Install

**Note:** Developer Mode can be disabled after installation. The app will continue to work.

### Option 2: Self-Sign the Package

**For users who prefer not to enable Developer Mode or have the Install button greyed out.**

**⚠️ Requires Administrator privileges**

1. Download **both** files from GitHub:
   - The MSIX package (e.g., `oathtool-1.2.3.msix`)
   - The fix script: `FIX-MSIX-INSTALL.ps1`
2. Place both files in the same directory
3. Right-click `FIX-MSIX-INSTALL.ps1` and select "Run as Administrator"
4. The script will:
   - Create a test certificate (CN=TestPublisher)
   - Install it to Trusted Root Certification Authorities
   - Sign the MSIX package
5. Double-click the MSIX to install

## Why Not Sign Packages in GitHub Actions?

Signing MSIX packages in CI/CD requires:

1. **A code signing certificate** ($200-500/year from a Certificate Authority)
2. **Storing the certificate securely** in GitHub Secrets
3. **Managing certificate passwords** and renewal

For an open-source project, this adds:
- **Cost:** Annual certificate fees
- **Complexity:** Secure credential management
- **Maintenance:** Certificate renewal every 1-3 years

**Alternative approaches:**

- **Microsoft Store:** If published to Microsoft Store, Microsoft signs packages for free
- **Self-signing:** Users sign packages themselves using `FIX-MSIX-INSTALL.ps1`
- **Developer Mode:** Windows built-in mechanism for unsigned package installation

## Files Related to MSIX Distribution

### Build Files
- `build-msix.ps1` - Main build script for creating MSIX packages
- `msix/AppxManifest.xml` - MSIX package manifest
- `msix/mapping.txt` - File mapping for package contents
- `msix/Assets/` - Application icons and logos
- `.github/workflows/main.yml` - GitHub Actions workflow (includes `build-msix` job)

### Installation Helper Scripts
- `FIX-MSIX-INSTALL.ps1` - All-in-one script for end users (creates cert, signs package)
- `create-test-cert-and-sign.ps1` - Developer script for local testing
- `install-cert-to-root.ps1` - Standalone script to install certificate to Trusted Root

### Documentation
- `README.rst` - Main documentation (includes MSIX installation instructions)
- `INSTALLING_UNSIGNED_MSIX.md` - Detailed installation guide for unsigned packages
- `MSIX_DISTRIBUTION.md` - This file (distribution strategy)

## For Contributors

### Testing MSIX Packages Locally

When testing MSIX packages during development:

1. Build the package:
   ```powershell
   pyinstaller oathtool.spec
   .\build-msix.ps1 -Version "1.0.0-test"
   ```

2. Install it:
   - **Option A:** Enable Developer Mode and double-click the MSIX
   - **Option B:** Run `FIX-MSIX-INSTALL.ps1` as Administrator

3. Verify installation:
   ```powershell
   Get-AppxPackage | Where-Object {$_.Name -like "*oathtool*"}
   ```

4. Uninstall after testing:
   ```powershell
   Get-AppxPackage *oathtool* | Remove-AppxPackage
   ```

### Creating a Release

To create a new release with MSIX package:

1. Update version in `pyproject.toml` and other relevant files
2. Commit changes:
   ```bash
   git add .
   git commit -m "Release v1.2.3"
   ```
3. Create and push tag:
   ```bash
   git tag v1.2.3
   git push origin main
   git push origin v1.2.3
   ```
4. GitHub Actions will automatically:
   - Run tests
   - Build MSIX package
   - Attach MSIX to the release
   - Publish to PyPI

## Security Considerations

### Unsigned Packages

**For end users:**
- Unsigned packages are safe to install if downloaded from trusted sources (GitHub Releases)
- Developer Mode slightly lowers security posture by allowing unsigned packages from any source
- Consider disabling Developer Mode after installation

**For the project:**
- GitHub Releases are the authoritative source
- Verify the repository URL: `https://github.com/jaraco/oathtool`
- Check commit signatures and release tags

### Self-Signed Certificates

The `FIX-MSIX-INSTALL.ps1` script creates a self-signed certificate and installs it to **Trusted Root Certification Authorities**. This means:

- ✅ Allows the MSIX package to install without Developer Mode
- ⚠️ Any package signed with that certificate will be trusted system-wide
- ⚠️ Requires Administrator privileges
- ⚠️ Certificate is stored in LocalMachine\Root (affects all users)

**Users can remove the certificate after installation:**
1. Press Win+R, type `certmgr.msc`
2. Go to: Trusted Root Certification Authorities → Certificates
3. Find "TestPublisher" and delete it

The installed app will continue to work after certificate removal.

## Future Improvements

Possible improvements to the distribution process:

1. **Microsoft Store Submission**
   - Pros: Free signing, automatic updates, wider distribution
   - Cons: One-time $19 fee, certification requirements, privacy policy needed

2. **Code Signing Certificate**
   - Pros: Professional appearance, no Developer Mode needed
   - Cons: $200-500/year cost, certificate management

3. **WinGet Package Manager**
   - Pros: Command-line installation, package manager integration
   - Cons: Requires package manifest, still needs signed or unsigned handling

4. **Chocolatey Package**
   - Pros: Popular Windows package manager, established ecosystem
   - Cons: Similar signing/trust requirements

## Summary

**Current approach:**
- ✅ Zero cost distribution
- ✅ Simple build process
- ✅ Automated via GitHub Actions
- ✅ Users have clear installation options
- ✅ Self-signing script available for users who need it

**Trade-offs:**
- ❌ Requires Developer Mode OR manual signing for installation
- ❌ Not as "professional" as signed packages
- ❌ Extra steps for end users compared to signed packages

For an open-source project, this is a reasonable trade-off that balances cost, complexity, and user experience.
