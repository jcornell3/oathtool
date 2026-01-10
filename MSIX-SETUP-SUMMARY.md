# MSIX Packaging Setup - Complete!

## What Was Created

### Local Build System
1. **msix/AppxManifest.xml** - MSIX package manifest
2. **msix/mapping.txt** - File mapping for package structure
3. **msix/Assets/** - Auto-generated placeholder logos (4 PNG files)
4. **build-msix.ps1** - PowerShell build script (in project root)
5. **msix/README.md** - Detailed documentation

### GitHub Actions Integration
- Updated `.github/workflows/main.yml` with new `build-msix` job
- Triggers on version tags (e.g., `v1.2.3`)
- Automatically builds and attaches MSIX to GitHub releases

## SDK Tools Detected

MakeAppx and SignTool were found at:
- `C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\`

## Quick Start

### Build Locally

```powershell
# Make sure you have dist\oathtool.exe built first
pyinstaller oathtool.spec

# Build MSIX package
.\build-msix.ps1 -Version "1.2.3"
```

Output: `dist\oathtool-1.2.3.msix`

### Build via GitHub Actions

```bash
# Tag and push
git tag v1.2.3
git push origin v1.2.3
```

The workflow will:
1. Build the PyInstaller executable
2. Create the MSIX package
3. Upload as artifact
4. Attach to GitHub release

## Test Build Results

Successfully created test package:
- **File**: `dist/oathtool-1.0.1.msix`
- **Size**: 7.4 KB
- **Status**: Package creation succeeded

## Next Steps

### For Local Development
1. Build your executable: `pyinstaller oathtool.spec`
2. Test MSIX build: `.\build-msix.ps1 -Version "1.0.0"`
3. Install unsigned package (requires Developer Mode):
   ```powershell
   Add-AppxPackage -Path "dist\oathtool-1.0.0.msix"
   ```

### For Production
1. Replace placeholder logos in `msix/Assets/` with branded images
2. (Optional) Get a code signing certificate for production distribution
3. Tag a release to trigger GitHub Actions build

### Optional: Code Signing

For local development testing:
```powershell
# Create self-signed certificate
$cert = New-SelfSignedCertificate -Type Custom -Subject "CN=Jason R. Coombs" `
    -KeyUsage DigitalSignature -FriendlyName "OathTool Dev Cert" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# Export to PFX
$pwd = ConvertTo-SecureString -String "YourPassword" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "cert.pfx" -Password $pwd

# Build and sign
.\build-msix.ps1 -Version "1.0.0" -Sign
```

## Customization

### Update Package Identity
Edit `msix/AppxManifest.xml`:
- Package name: `<Identity Name="com.jaraco.oathtool">`
- Publisher: `Publisher="CN=Jason R. Coombs"`
- Display name, description, etc.

### Custom Logos
Replace auto-generated images in `msix/Assets/`:
- **StoreLogo.png** (50x50)
- **Square44x44Logo.png** (44x44)
- **Square150x150Logo.png** (150x150)
- **Wide310x150Logo.png** (310x150)

## Documentation

See `msix/README.md` for detailed information on:
- Installation requirements
- Troubleshooting
- Advanced configuration
- Package signing

## Support

For MSIX packaging issues, see:
- [MSIX Documentation](https://docs.microsoft.com/windows/msix/)
- [App Manifest Schema](https://docs.microsoft.com/uwp/schemas/appxpackage/uapmanifestschema/schema-root)
