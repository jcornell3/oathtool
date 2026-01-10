# ALL-IN-ONE FIX FOR MSIX INSTALLATION
#
# This script is for users who downloaded the MSIX package from GitHub Releases
# and have the Install button greyed out.
#
# USAGE:
# 1. Download both the MSIX package and this script from GitHub
# 2. Place them in the same directory
# 3. Right-click this file and select "Run as Administrator"
#
# The script will:
# - Create a test certificate (CN=TestPublisher)
# - Install it to Trusted Root Certification Authorities
# - Sign the MSIX package
# - Make the Install button work!

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MSIX Installation Fix for OathTool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Must run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To fix:" -ForegroundColor Yellow
    Write-Host "1. Right-click this script file (FIX-MSIX-INSTALL.ps1)" -ForegroundColor White
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 1: Create certificate
Write-Host "[1/4] Creating test certificate..." -ForegroundColor Yellow

$cert = New-SelfSignedCertificate `
    -Type Custom `
    -Subject "CN=TestPublisher" `
    -KeyUsage DigitalSignature `
    -FriendlyName "OathTool MSIX Test Certificate" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

Write-Host "      Certificate created! Thumbprint: $($cert.Thumbprint)" -ForegroundColor Green

# Step 2: Export certificate
Write-Host "[2/4] Exporting certificate..." -ForegroundColor Yellow

$certPath = Join-Path $PSScriptRoot "oathtool-test-cert.cer"
Export-Certificate -Cert $cert -FilePath $certPath | Out-Null
Write-Host "      Exported to: $certPath" -ForegroundColor Green

# Step 3: Install to Trusted Root
Write-Host "[3/4] Installing certificate to Trusted Root..." -ForegroundColor Yellow
Write-Host "      (This allows the MSIX package to be trusted)" -ForegroundColor Gray

Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\Root" | Out-Null
Write-Host "      Certificate installed to Trusted Root!" -ForegroundColor Green

# Step 4: Sign the MSIX package
Write-Host "[4/4] Signing MSIX package..." -ForegroundColor Yellow

# Find SignTool
$signToolPaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
)

$signTool = $null
foreach ($path in $signToolPaths) {
    if (Test-Path $path) {
        $signTool = $path
        break
    }
}

if (-not $signTool) {
    Write-Host "      ERROR: SignTool not found!" -ForegroundColor Red
    Write-Host "      Please install Windows SDK" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Find MSIX package in current directory or dist subdirectory
$msixPath = $null
$searchPaths = @(
    (Join-Path $PSScriptRoot "*.msix"),
    (Join-Path $PSScriptRoot "dist\*.msix")
)

foreach ($searchPath in $searchPaths) {
    $found = Get-Item $searchPath -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $msixPath = $found.FullName
        break
    }
}

if (-not $msixPath) {
    Write-Host "      ERROR: No MSIX package found!" -ForegroundColor Red
    Write-Host "      Please place the oathtool MSIX file in the same directory as this script." -ForegroundColor Yellow
    Write-Host "      Or place it in a 'dist' subdirectory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "      Found MSIX package: $(Split-Path $msixPath -Leaf)" -ForegroundColor Gray

& $signTool sign /fd SHA256 /sha1 $cert.Thumbprint /td SHA256 $msixPath 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "      Package signed successfully!" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Signing failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Success!
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SUCCESS! Installation is ready" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The MSIX package is now signed and ready to install!" -ForegroundColor White
Write-Host ""
Write-Host "To install:" -ForegroundColor Cyan
Write-Host "  1. Double-click: $(Split-Path $msixPath -Leaf)" -ForegroundColor White
Write-Host "  2. Click the 'Install' button (should now work!)" -ForegroundColor White
Write-Host ""
Write-Host "Or via PowerShell:" -ForegroundColor Cyan
Write-Host "  Add-AppxPackage -Path '$msixPath'" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Security Note:" -ForegroundColor Yellow
Write-Host "The test certificate was installed to Trusted Root." -ForegroundColor Gray
Write-Host "To remove it later (optional):" -ForegroundColor Gray
Write-Host "  1. Press Win+R, type 'certmgr.msc'" -ForegroundColor Gray
Write-Host "  2. Go to: Trusted Root Certification Authorities > Certificates" -ForegroundColor Gray
Write-Host "  3. Find 'TestPublisher' and delete it" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit"
