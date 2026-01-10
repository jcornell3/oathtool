# Create test certificate and sign MSIX package
$ErrorActionPreference = "Stop"

Write-Host "`n=== Creating Test Certificate ===" -ForegroundColor Cyan

# Create certificate matching manifest publisher
$cert = New-SelfSignedCertificate `
    -Type Custom `
    -Subject "CN=TestPublisher" `
    -KeyUsage DigitalSignature `
    -FriendlyName "OathTool Test Certificate" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

Write-Host "Certificate created!" -ForegroundColor Green
Write-Host "Thumbprint: $($cert.Thumbprint)"

# Export certificate
$certPath = "oathtool-test-cert.cer"
Export-Certificate -Cert $cert -FilePath $certPath | Out-Null
Write-Host "Certificate exported to: $certPath"

# Install to Trusted People store
Write-Host "`nInstalling certificate..." -ForegroundColor Cyan
Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\CurrentUser\TrustedPeople" | Out-Null
Write-Host "Certificate installed to Trusted People store!" -ForegroundColor Green

# Find SignTool
Write-Host "`nLooking for SignTool..." -ForegroundColor Cyan
$signToolPaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe"
)

$signTool = $null
foreach ($path in $signToolPaths) {
    if (Test-Path $path) {
        $signTool = $path
        Write-Host "Found: $signTool" -ForegroundColor Green
        break
    }
}

if (-not $signTool) {
    Write-Error "SignTool not found. Install Windows SDK."
    exit 1
}

# Sign the MSIX
$msixPath = "dist\oathtool-1.0.2.msix"

if (-not (Test-Path $msixPath)) {
    Write-Error "MSIX not found: $msixPath"
    exit 1
}

Write-Host "`nSigning MSIX package..." -ForegroundColor Cyan
& $signTool sign /fd SHA256 /sha1 $cert.Thumbprint /td SHA256 $msixPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== SUCCESS! ===" -ForegroundColor Green
    Write-Host "Package signed: $msixPath"
    Write-Host "`nYou can now install the package!"
    Write-Host "Try double-clicking: $msixPath" -ForegroundColor Cyan
} else {
    Write-Error "Signing failed"
}
