# PowerShell script to create a self-signed certificate and sign the MSIX package
# Run as Administrator

param(
    [string]$Version = "1.0.1"
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Creating Self-Signed Certificate for MSIX ===" -ForegroundColor Cyan

# Create self-signed certificate matching the manifest Publisher
$cert = New-SelfSignedCertificate `
    -Type Custom `
    -Subject "CN=Jason R. Coombs" `
    -KeyUsage DigitalSignature `
    -FriendlyName "OathTool MSIX Signing" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

Write-Host "Certificate created successfully!" -ForegroundColor Green
Write-Host "Thumbprint: $($cert.Thumbprint)"

# Export certificate for installation
$certPath = Join-Path $PSScriptRoot "oathtool-cert.cer"
Export-Certificate -Cert $cert -FilePath $certPath | Out-Null
Write-Host "Certificate exported to: $certPath"

# Install certificate to Trusted People (safer than Trusted Root for testing)
Write-Host "`nInstalling certificate to Trusted People store..." -ForegroundColor Cyan
Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\CurrentUser\TrustedPeople" | Out-Null
Write-Host "Certificate installed successfully!" -ForegroundColor Green

# Find SignTool
Write-Host "`nLooking for SignTool..." -ForegroundColor Cyan
$signToolPaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
)

$signTool = $null
foreach ($path in $signToolPaths) {
    if (Test-Path $path) {
        $signTool = $path
        Write-Host "Found SignTool at: $signTool" -ForegroundColor Green
        break
    }
}

if (-not $signTool) {
    Write-Error "SignTool not found. Please install Windows SDK."
    exit 1
}

# Sign the MSIX package
$msixPath = Join-Path $PSScriptRoot "dist\oathtool-$Version.msix"

if (-not (Test-Path $msixPath)) {
    Write-Error "MSIX package not found at: $msixPath"
    exit 1
}

Write-Host "`nSigning MSIX package..." -ForegroundColor Cyan
$signArgs = @(
    "sign",
    "/fd", "SHA256",
    "/sha1", $cert.Thumbprint,
    "/td", "SHA256",
    "/v",
    $msixPath
)

& $signTool $signArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nPackage signed successfully!" -ForegroundColor Green
    Write-Host "You can now install: $msixPath" -ForegroundColor Green
    Write-Host "`nTo install, run:" -ForegroundColor Cyan
    Write-Host "  Add-AppxPackage -Path '$msixPath'" -ForegroundColor White
    Write-Host "`nOr double-click the .msix file" -ForegroundColor Cyan
} else {
    Write-Error "Signing failed with exit code: $LASTEXITCODE"
    exit 1
}

Write-Host "`n=== Complete! ===" -ForegroundColor Green
