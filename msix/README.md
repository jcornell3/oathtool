# MSIX Package Build Instructions

This directory contains files for packaging OathTool as an MSIX package for Windows installation.

## Files

- **AppxManifest.xml** - MSIX package manifest with app metadata
- **mapping.txt** - File mapping configuration for MakeAppx
- **Assets/** - Logo images for the MSIX package (auto-generated)
- **../build-msix.ps1** - PowerShell build script (in project root)

## Building Locally

### Prerequisites

1. Windows SDK installed (includes MakeAppx.exe and SignTool.exe)
   - The script automatically detects SDK tools in standard locations
2. PyInstaller executable already built at `dist\oathtool.exe`
   - Build with: `pyinstaller oathtool.spec`

### Build Command

```powershell
# Basic build (default version 1.0.0)
.\build-msix.ps1

# Specify version
.\build-msix.ps1 -Version "1.2.3"

# Build with signing (requires certificate)
.\build-msix.ps1 -Version "1.2.3" -Sign

# Custom SDK paths
.\build-msix.ps1 -MakeAppxPath "C:\path\to\makeappx.exe" -SignToolPath "C:\path\to\signtool.exe"
```

### Output

The MSIX package will be created at:
```
dist\oathtool-<version>.msix
```

## GitHub Actions Build

The MSIX package is automatically built when you push a version tag:

```bash
git tag v1.2.3
git push origin v1.2.3
```

The workflow will:
1. Build the PyInstaller executable
2. Create the MSIX package
3. Upload it as a workflow artifact
4. Attach it to the GitHub release

## Installing the Package

### For Development/Testing (Unsigned)

**⚠️ The package is unsigned and requires Developer Mode.**

**Quick Steps:**

1. **Enable Developer Mode** in Windows Settings:
   - **Windows 11:** Settings → Privacy & security → For developers → Developer Mode
   - **Windows 10:** Settings → Update & Security → For developers → Developer mode

2. **Install the package:**
   ```powershell
   Add-AppxPackage -Path "dist\oathtool-1.2.3.msix"
   ```
   Or simply double-click the .msix file.

**For detailed installation instructions, troubleshooting, and alternative methods
(including self-signing), see:** `../INSTALLING_UNSIGNED_MSIX.md`

### For Production (Signed)

For distribution outside the Microsoft Store, you'll need:

1. A valid code signing certificate
2. Update `build-msix.ps1` with certificate details
3. Build with `-Sign` flag

**Creating a self-signed certificate for testing:**

```powershell
$cert = New-SelfSignedCertificate -Type Custom -Subject "CN=Jason R. Coombs" `
    -KeyUsage DigitalSignature -FriendlyName "OathTool Dev Cert" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# Export certificate
$pwd = ConvertTo-SecureString -String "YourPassword" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "cert.pfx" -Password $pwd
```

## Customizing

### Update Version

The version is automatically updated from the build script parameter or GitHub tag. The manifest uses a 4-part version (Major.Minor.Patch.0).

### Custom Logos

Replace the auto-generated placeholder images in `Assets/` with your own:
- StoreLogo.png (50x50)
- Square44x44Logo.png (44x44)
- Square150x150Logo.png (150x150)
- Wide310x150Logo.png (310x150)

### Package Identity

Edit `AppxManifest.xml` to change:
- Package name: `Identity Name="com.jaraco.oathtool"`
- Publisher: `Publisher="CN=Jason R. Coombs"`
- Display name, description, etc.

## Troubleshooting

### "makeappx.exe not found"

Install the Windows SDK from https://developer.microsoft.com/windows/downloads/windows-sdk/

### "Cannot install unsigned package"

Enable Developer Mode in Windows Settings, or sign the package with a valid certificate.

### "Version conflict"

Uninstall the existing version first:
```powershell
Remove-AppxPackage -Package "com.jaraco.oathtool_*"
```

## Additional Resources

- [MSIX Packaging Documentation](https://docs.microsoft.com/windows/msix/)
- [App Manifest Schema](https://docs.microsoft.com/uwp/schemas/appxpackage/uapmanifestschema/schema-root)
