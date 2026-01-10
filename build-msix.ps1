# PowerShell script to build MSIX package for OathTool
# Usage: .\build-msix.ps1 [-Version "1.2.3"] [-Sign]

param(
    [string]$Version = "1.0.0",
    [switch]$Sign = $false,
    [string]$MakeAppxPath = "",
    [string]$SignToolPath = ""
)

$ErrorActionPreference = "Stop"

# Find Windows SDK tools if not provided
if (-not $MakeAppxPath) {
    $sdkPaths = @(
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\makeappx.exe",
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\makeappx.exe",
        "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\makeappx.exe"
    )
    foreach ($path in $sdkPaths) {
        if (Test-Path $path) {
            $MakeAppxPath = $path
            Write-Host "Found makeappx.exe at: $MakeAppxPath" -ForegroundColor Green
            break
        }
    }
    if (-not $MakeAppxPath) {
        Write-Error "makeappx.exe not found. Please install Windows SDK or provide path with -MakeAppxPath"
        exit 1
    }
}

if ($Sign -and -not $SignToolPath) {
    $sdkPaths = @(
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
    )
    foreach ($path in $sdkPaths) {
        if (Test-Path $path) {
            $SignToolPath = $path
            Write-Host "Found signtool.exe at: $SignToolPath" -ForegroundColor Green
            break
        }
    }
    if (-not $SignToolPath) {
        Write-Error "signtool.exe not found. Please install Windows SDK or provide path with -SignToolPath"
        exit 1
    }
}

# Paths
$rootDir = $PSScriptRoot
$msixDir = Join-Path $rootDir "msix"
$distDir = Join-Path $rootDir "dist"
$assetsDir = Join-Path $msixDir "Assets"
$outputDir = Join-Path $rootDir "dist"
$manifestPath = Join-Path $msixDir "AppxManifest.xml"

# Verify dist\oathtool.exe exists
$exePath = Join-Path $distDir "oathtool.exe"
if (-not (Test-Path $exePath)) {
    Write-Error "oathtool.exe not found at $exePath. Please build it first with PyInstaller."
    exit 1
}

Write-Host "`nBuilding MSIX package for OathTool v$Version" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Create Assets directory if it doesn't exist
if (-not (Test-Path $assetsDir)) {
    New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null
}

# Generate placeholder logos if they don't exist
function New-PlaceholderImage {
    param([string]$Path, [int]$Width, [int]$Height)

    if (Test-Path $Path) {
        Write-Host "  Using existing: $(Split-Path $Path -Leaf)" -ForegroundColor Gray
        return
    }

    Write-Host "  Creating placeholder: $(Split-Path $Path -Leaf)" -ForegroundColor Yellow

    # Create a simple PNG placeholder using .NET
    Add-Type -AssemblyName System.Drawing
    $bitmap = New-Object System.Drawing.Bitmap($Width, $Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)

    # Fill with a simple color
    $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(0, 120, 212))
    $graphics.FillRectangle($brush, 0, 0, $Width, $Height)

    # Add text
    $font = New-Object System.Drawing.Font("Arial", [int]($Height / 8), [System.Drawing.FontStyle]::Bold)
    $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
    $text = "OTP"
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rect = New-Object System.Drawing.RectangleF(0, 0, $Width, $Height)
    $graphics.DrawString($text, $font, $textBrush, $rect, $format)

    # Save
    $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
}

Write-Host "Generating logo assets..." -ForegroundColor Cyan
New-PlaceholderImage -Path (Join-Path $assetsDir "StoreLogo.png") -Width 50 -Height 50
New-PlaceholderImage -Path (Join-Path $assetsDir "Square44x44Logo.png") -Width 44 -Height 44
New-PlaceholderImage -Path (Join-Path $assetsDir "Square150x150Logo.png") -Width 150 -Height 150
New-PlaceholderImage -Path (Join-Path $assetsDir "Wide310x150Logo.png") -Width 310 -Height 150

# Update version in manifest
Write-Host "`nUpdating manifest version to $Version.0..." -ForegroundColor Cyan
$manifestContent = Get-Content $manifestPath -Raw
# Use a more specific pattern to only match the Identity element's Version attribute
$versionPattern = '(<Identity[^>]*Version=")[^"]*(")'
$manifestContent = $manifestContent -replace $versionPattern, "`${1}$Version.0`${2}"
Set-Content -Path $manifestPath -Value $manifestContent -NoNewline

# Build MSIX package
$msixFile = Join-Path $outputDir "oathtool-$Version.msix"
Write-Host "`nBuilding MSIX package..." -ForegroundColor Cyan
Write-Host "  Output: $msixFile" -ForegroundColor Gray

& $MakeAppxPath pack /d $msixDir /p $msixFile /nv /o

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create MSIX package"
    exit 1
}

Write-Host "`nMSIX package created successfully!" -ForegroundColor Green
Write-Host "  Location: $msixFile" -ForegroundColor Green
Write-Host "  Size: $([math]::Round((Get-Item $msixFile).Length / 1MB, 2)) MB" -ForegroundColor Green

# Sign the package if requested
if ($Sign) {
    Write-Host "`nSigning package..." -ForegroundColor Cyan
    Write-Host "  Note: This requires a valid code signing certificate" -ForegroundColor Yellow
    Write-Host "  For development/testing, you can create a self-signed certificate:" -ForegroundColor Yellow
    Write-Host "  New-SelfSignedCertificate -Type Custom -Subject 'CN=Jason R. Coombs' -KeyUsage DigitalSignature -FriendlyName 'OathTool Dev Cert' -CertStoreLocation 'Cert:\CurrentUser\My' -TextExtension @('2.5.29.37={text}1.3.6.1.5.5.7.3.3', '2.5.29.19={text}')" -ForegroundColor Gray

    # Try to sign (will fail if no certificate is available)
    try {
        & $SignToolPath sign /fd SHA256 /a /f "cert.pfx" /p "password" $msixFile
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Package signed successfully!" -ForegroundColor Green
        }
    } catch {
        Write-Warning "Signing failed. For testing, you can install unsigned packages by enabling Developer Mode in Windows Settings."
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "`nTo install (Developer Mode required for unsigned packages):" -ForegroundColor Cyan
Write-Host "  Add-AppxPackage -Path '$msixFile'" -ForegroundColor White
Write-Host "`nOr double-click the .msix file to install." -ForegroundColor Cyan
