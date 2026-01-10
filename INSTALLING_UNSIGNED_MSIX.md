# Installing Unsigned MSIX Packages on Windows

Since the oathtool MSIX package is not signed with a trusted certificate, Windows requires special steps to install it. This guide covers all methods for installing unsigned MSIX packages.

---

## Quick Solution: Enable Developer Mode

### Step 1: Enable Developer Mode

**Windows 11:**
1. Open **Settings** (Win + I)
2. Go to **Privacy & security** → **For developers**
3. Toggle **Developer Mode** to **On**
4. Click **Yes** on the confirmation dialog
5. Wait for Windows to install developer mode packages

**Windows 10:**
1. Open **Settings** (Win + I)
2. Go to **Update & Security** → **For developers**
3. Select **Developer mode**
4. Click **Yes** on the confirmation dialog
5. Wait for installation to complete

### Step 2: Install the MSIX Package

**Method 1: Double-click**
1. Double-click the `.msix` file
2. Click **Install**
3. Wait for installation to complete
4. The app will be available in Start Menu

**Method 2: PowerShell**
```powershell
Add-AppxPackage -Path "C:\path\to\oathtool-1.0.0.msix"
```

**Method 3: Right-click**
1. Right-click the `.msix` file
2. Select **Install**
3. Follow the prompts

---

## Alternative: Install Without Developer Mode

If you can't or don't want to enable Developer Mode, you need to:

1. Create a self-signed certificate
2. Install the certificate to Trusted Root
3. Sign the MSIX package
4. Install the signed package

### Step-by-Step Process

#### 1. Create Self-Signed Certificate

Open PowerShell as Administrator:

```powershell
# Create self-signed certificate
$cert = New-SelfSignedCertificate `
    -Type Custom `
    -Subject "CN=OathTool Developer Certificate" `
    -KeyUsage DigitalSignature `
    -FriendlyName "OathTool Development" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# Export certificate
$password = ConvertTo-SecureString -String "YourPassword123" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "oathtool-cert.pfx" -Password $password

# Export public key
Export-Certificate -Cert $cert -FilePath "oathtool-cert.cer"

Write-Host "`nCertificate created successfully!"
Write-Host "Thumbprint: $($cert.Thumbprint)"
```

#### 2. Install Certificate to Trusted Root

**Option A: Using PowerShell (Administrator)**
```powershell
# Import to Trusted Root
$cert = Get-PfxCertificate -FilePath "oathtool-cert.cer"
Import-Certificate -FilePath "oathtool-cert.cer" -CertStoreLocation "Cert:\LocalMachine\Root"

Write-Host "Certificate installed to Trusted Root"
```

**Option B: Using Certificate Manager GUI**
1. Double-click `oathtool-cert.cer`
2. Click **Install Certificate**
3. Select **Local Machine** → Click **Next**
4. Click **Yes** on UAC prompt
5. Select **Place all certificates in the following store**
6. Click **Browse** → Select **Trusted Root Certification Authorities**
7. Click **OK** → **Next** → **Finish**

**Security Warning:** Installing to Trusted Root requires Administrator privileges and allows the certificate to sign any code on your system.

#### 3. Sign the MSIX Package

Find SignTool.exe (part of Windows SDK):

```powershell
# Find SignTool
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"

# Verify it exists
if (Test-Path $signtool) {
    Write-Host "Found SignTool at: $signtool"
} else {
    Write-Host "SignTool not found. Install Windows SDK."
    exit
}

# Sign the MSIX package
& $signtool sign /fd SHA256 /a /f "oathtool-cert.pfx" /p "YourPassword123" "oathtool-1.0.0.msix"

Write-Host "Package signed successfully!"
```

#### 4. Install the Signed Package

Now you can install without Developer Mode:

```powershell
Add-AppxPackage -Path "oathtool-1.0.0.msix"
```

Or double-click the `.msix` file.

---

## Troubleshooting Common Issues

### Issue 1: "This app package is not signed with a trusted certificate"

**Solution:** Enable Developer Mode or sign the package with a trusted certificate.

```powershell
# Quick check if Developer Mode is enabled
Get-WindowsDeveloperLicense
# If it returns a license, Developer Mode is enabled
```

### Issue 2: "Add-AppxPackage: Deployment failed..."

**Check the error code:**

```powershell
Add-AppxPackage -Path "oathtool-1.0.0.msix" -Verbose
```

**Common error codes:**

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 0x80073D01 | Developer Mode not enabled | Enable Developer Mode |
| 0x80073CF0 | Package already installed | Uninstall old version first |
| 0x800B0109 | Certificate chain invalid | Install certificate to Trusted Root |
| 0x80073CFB | Package architecture mismatch | Check if package is x64/x86/ARM |

### Issue 3: "Developer Mode is not available on this edition"

Some Windows editions (like Windows 10/11 in S Mode) don't support Developer Mode.

**Solution 1:** Switch out of S Mode
1. Open Microsoft Store
2. Search for "Switch out of S Mode"
3. Follow instructions to switch

**Solution 2:** Use the portable executable
Instead of MSIX, just use `oathtool.exe` directly - no installation needed!

### Issue 4: Package installed but not appearing

**Refresh Start Menu:**
```powershell
# Restart Windows Explorer
Stop-Process -Name explorer -Force
Start-Process explorer
```

**Or check installed packages:**
```powershell
Get-AppxPackage | Where-Object {$_.Name -like "*oathtool*"}
```

---

## Uninstalling the Package

### Method 1: Settings
1. Open **Settings** → **Apps** → **Installed apps**
2. Find **OathTool**
3. Click **⋮** (three dots) → **Uninstall**

### Method 2: PowerShell
```powershell
# Find the package
Get-AppxPackage | Where-Object {$_.Name -like "*oathtool*"}

# Uninstall by package full name
Remove-AppxPackage -Package "com.jaraco.oathtool_1.0.0.0_x64__xxxxx"

# Or simple version
Get-AppxPackage *oathtool* | Remove-AppxPackage
```

---

## For Production/Distribution

If you're distributing this tool to others, you have several options:

### Option 1: Code Signing Certificate (Recommended)

Purchase a code signing certificate from a Certificate Authority:

**Trusted CAs:**
- DigiCert ($200-500/year)
- Sectigo ($100-300/year)
- GlobalSign ($200-400/year)

**Benefits:**
- Users can install without Developer Mode
- No security warnings
- Professional appearance
- Required for Microsoft Store

**Process:**
1. Purchase certificate from CA
2. Verify your identity (required by CA)
3. Receive certificate file (.pfx)
4. Sign MSIX with certificate
5. Distribute signed package

```powershell
# Sign with purchased certificate
signtool sign /fd SHA256 /f "MyCodeSignCert.pfx" /p "password" "oathtool-1.0.0.msix"
```

### Option 2: Microsoft Store (Free Distribution)

Publishing to Microsoft Store provides:
- ✅ Microsoft signs the package for you
- ✅ Automatic updates
- ✅ No Developer Mode needed for users
- ✅ Wider distribution

**Requirements:**
- Microsoft Partner Center account ($19 one-time fee for individuals)
- App certification requirements
- Privacy policy and terms of use

### Option 3: Distribute Portable EXE (Simplest)

Just share `oathtool.exe` - no installation needed!

**Pros:**
- No MSIX complexity
- No certificates needed
- Works on any Windows
- No installation required

**Cons:**
- No auto-updates
- No Start Menu integration
- Not "installed" in traditional sense

---

## Security Considerations

### Developer Mode Security Impact

**What Developer Mode allows:**
- Installation of unsigned MSIX packages
- Sideloading apps from any source
- Developer debugging features
- PowerShell remoting (if enabled)

**Security risks:**
- Slightly lower security posture
- Malicious unsigned apps could be installed
- Not recommended for enterprise/managed devices

**Recommendation:**
- Use Developer Mode only on development machines
- For production, use signed packages or portable EXE

### Self-Signed Certificate Risks

**Installing to Trusted Root means:**
- ⚠️ Any package signed with that certificate will be trusted
- ⚠️ If certificate is compromised, attacker can sign malicious code
- ⚠️ Applies system-wide (all users)

**Best practices:**
- Only install self-signed certificates you created yourself
- Use password-protected certificate files
- Delete certificate when no longer needed
- Don't share certificate files

**Remove certificate when done:**
```powershell
# List certificates
Get-ChildItem Cert:\LocalMachine\Root | Where-Object {$_.Subject -like "*OathTool*"}

# Remove by thumbprint
Remove-Item Cert:\LocalMachine\Root\[THUMBPRINT]
```

---

## Quick Reference Card

### Installing Unsigned MSIX

```
┌─────────────────────────────────────────────────────┐
│  Installing oathtool-1.0.0.msix                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Easy Method (Developer Mode):                     │
│  1. Settings → For developers                      │
│  2. Enable Developer Mode                          │
│  3. Double-click .msix file                        │
│                                                     │
│  PowerShell Method:                                │
│    Add-AppxPackage -Path "oathtool-1.0.0.msix"    │
│                                                     │
│  Alternative (Portable):                           │
│    Just use oathtool.exe - no install needed!     │
│                                                     │
│  Check if installed:                               │
│    Get-AppxPackage | Where Name -like *oathtool*  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## FAQ

**Q: Is Developer Mode safe?**
A: Yes, for personal development machines. Not recommended for enterprise/production systems.

**Q: Can I disable Developer Mode after installing?**
A: Yes, the app will continue to work. Developer Mode is only needed for installation.

**Q: Will Windows Defender flag this?**
A: Unsigned executables might trigger SmartScreen. Click "More info" → "Run anyway" if needed.

**Q: Can I install on multiple computers?**
A: Yes, but each needs Developer Mode enabled or the signed package approach.

**Q: Do I need administrator rights?**
A: No for installing with Developer Mode. Yes for signing and installing certificates to Trusted Root.

**Q: Can I use this on a company/work computer?**
A: Check with your IT department. Many companies block Developer Mode and unsigned apps.

**Q: Is the portable .exe easier?**
A: Yes! For personal use, `oathtool.exe` requires no installation or special settings.

---

## Recommended Approach by Use Case

| Use Case | Recommended Method | Why |
|----------|-------------------|-----|
| **Personal use** | Portable .exe | Simplest, no installation |
| **Development/testing** | Developer Mode + MSIX | Full Windows integration |
| **Multiple developers** | Self-signed cert + MSIX | Consistent installation |
| **Public distribution** | Code signed MSIX | Professional, trusted |
| **Microsoft Store** | Store submission | Free signing, auto-updates |
| **Enterprise deployment** | Code signed MSIX | IT policy compliant |

---

## Additional Resources

- **Microsoft MSIX Documentation:** https://docs.microsoft.com/windows/msix/
- **Developer Mode Guide:** https://docs.microsoft.com/windows/apps/get-started/enable-your-device-for-development
- **Code Signing:** https://docs.microsoft.com/windows/win32/appxpkg/how-to-sign-a-package-using-signtool
- **Certificate Management:** https://docs.microsoft.com/windows-hardware/drivers/install/managing-the-signing-process

---

**Summary:** For personal use, the easiest approach is enabling Developer Mode. For distribution to others, consider using the portable `oathtool.exe` or investing in a code signing certificate.
