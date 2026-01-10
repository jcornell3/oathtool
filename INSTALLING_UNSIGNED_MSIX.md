# Installing Unsigned MSIX Packages on Windows

Since the oathtool MSIX package is not signed with a trusted certificate, Windows requires special steps to install it. This guide covers all methods for installing unsigned MSIX packages.

---

## ⚠️ Install Button Greyed Out?

If the **Install** button is greyed out even with Developer Mode enabled, the package needs to be signed first.

**Quick fix for users who downloaded from GitHub:**

1. Download both files from the `GitHub repository <https://github.com/jcornell3/oathtool>`_:
   - The MSIX package (e.g., ``oathtool-1.0.2.msix``)
   - The fix script: ``FIX-MSIX-INSTALL.ps1``
2. Place both files in the same directory
3. **Right-click** ``FIX-MSIX-INSTALL.ps1``
4. Select **"Run as Administrator"**
5. Wait for the script to complete (creates certificate, installs to Trusted Root, signs package)
6. Double-click the MSIX file to install

**What the script does:**
1. Creates a test certificate matching the package publisher (CN=TestPublisher)
2. Installs it to your Trusted Root Certification Authorities store (requires Admin)
3. Signs the MSIX package
4. Provides installation instructions

**Then try installing again** - the Install button should now work!

**Note:** The script requires Administrator privileges because it installs the certificate
to the LocalMachine\Root store, which allows all users on the system to trust packages
signed with this certificate.

---

## Recommended Solution: Sign the Package

**Important:** Simply enabling Developer Mode is **NOT sufficient**. The MSIX package must be
signed with a certificate that is installed in Trusted Root Certification Authorities.

The easiest approach is to use the provided script to sign the package:

### Step 1: Download Required Files

1. Download the MSIX package from GitHub Releases
2. Download ``FIX-MSIX-INSTALL.ps1`` from the repository
3. Place both in the same directory

### Step 2: Run the Fix Script

1. **Right-click** ``FIX-MSIX-INSTALL.ps1``
2. Select **"Run as Administrator"**
3. Wait for the script to complete (creates cert, installs to Trusted Root, signs package)

### Step 3: Install the MSIX Package

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

## Alternative: Manual Signing Process

If you prefer to sign the package manually instead of using `FIX-MSIX-INSTALL.ps1`, you can
follow these steps:

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

**Q: Do I need Developer Mode?**
A: No, Developer Mode is **not** sufficient for unsigned MSIX packages. You must sign the package using `FIX-MSIX-INSTALL.ps1`.

**Q: Will Windows Defender flag this?**
A: Unsigned executables might trigger SmartScreen. Click "More info" → "Run anyway" if needed.

**Q: Can I install on multiple computers?**
A: Yes, but you must run `FIX-MSIX-INSTALL.ps1` on each computer to sign the package.

**Q: Do I need administrator rights?**
A: Yes, the `FIX-MSIX-INSTALL.ps1` script requires Administrator privileges to install the certificate to Trusted Root.

**Q: Can I use this on a company/work computer?**
A: Check with your IT department. Installing certificates to Trusted Root requires Administrator privileges, which are often restricted on corporate computers. The portable `.exe` may be a better option.

**Q: Is the portable .exe easier?**
A: Yes! For personal use, `oathtool.exe` requires no installation or special settings.

---

## Recommended Approach by Use Case

| Use Case | Recommended Method | Why |
|----------|-------------------|-----|
| **Personal use** | Portable .exe | Simplest, no installation, no Admin required |
| **Development/testing** | Self-signed MSIX via FIX-MSIX-INSTALL.ps1 | Full Windows integration |
| **Multiple developers** | Self-signed cert + MSIX | Each user runs fix script once |
| **Public distribution** | Code signed MSIX | Professional, no end-user signing needed |
| **Microsoft Store** | Store submission | Free signing, auto-updates |
| **Enterprise deployment** | Code signed MSIX | IT policy compliant |

---

## Additional Resources

- **Microsoft MSIX Documentation:** https://docs.microsoft.com/windows/msix/
- **Developer Mode Guide:** https://docs.microsoft.com/windows/apps/get-started/enable-your-device-for-development
- **Code Signing:** https://docs.microsoft.com/windows/win32/appxpkg/how-to-sign-a-package-using-signtool
- **Certificate Management:** https://docs.microsoft.com/windows-hardware/drivers/install/managing-the-signing-process

---

**Summary:** For personal use, the easiest approach is using the portable `oathtool.exe` (no installation needed). For MSIX installation, run `FIX-MSIX-INSTALL.ps1` as Administrator to sign the package. For distributing to many users, consider investing in a code signing certificate or publishing to the Microsoft Store.
