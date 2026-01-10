# Install test certificate to Trusted Root (requires Administrator)
# Run this as Administrator

$ErrorActionPreference = "Stop"

Write-Host "`n=== Installing Certificate to Trusted Root ===" -ForegroundColor Cyan
Write-Host "This requires Administrator privileges!" -ForegroundColor Yellow

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`nERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "`nTo run as Administrator:" -ForegroundColor Yellow
    Write-Host "1. Right-click PowerShell" -ForegroundColor White
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host "3. Navigate to: $PSScriptRoot" -ForegroundColor White
    Write-Host "4. Run: .\install-cert-to-root.ps1" -ForegroundColor White
    exit 1
}

# Check if certificate file exists
$certPath = Join-Path $PSScriptRoot "oathtool-test-cert.cer"

if (-not (Test-Path $certPath)) {
    Write-Host "`nCertificate file not found: $certPath" -ForegroundColor Red
    Write-Host "Please run create-test-cert-and-sign.ps1 first!" -ForegroundColor Yellow
    exit 1
}

# Import to Trusted Root (Local Machine)
Write-Host "`nImporting certificate to Trusted Root Certification Authorities..." -ForegroundColor Cyan
Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\Root" | Out-Null

Write-Host "`n=== SUCCESS! ===" -ForegroundColor Green
Write-Host "Certificate installed to Trusted Root" -ForegroundColor Green
Write-Host "`nYou can now install the MSIX package:" -ForegroundColor Cyan
Write-Host "  Double-click: dist\oathtool-1.0.2.msix" -ForegroundColor White
Write-Host "`nOr via PowerShell:" -ForegroundColor Cyan
Write-Host "  Add-AppxPackage -Path 'dist\oathtool-1.0.2.msix'" -ForegroundColor White

Write-Host "`n=== Security Note ===" -ForegroundColor Yellow
Write-Host "Installing to Trusted Root allows this certificate to sign any code." -ForegroundColor Yellow
Write-Host "To remove the certificate later:" -ForegroundColor Yellow
Write-Host "  certmgr.msc -> Trusted Root -> Certificates -> Find 'TestPublisher' -> Delete" -ForegroundColor White
