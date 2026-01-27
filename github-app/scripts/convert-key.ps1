# PowerShell script to convert GitHub App private key to .env format
# Usage: .\convert-key.ps1 path\to\private-key.pem

param(
    [Parameter(Mandatory=$true)]
    [string]$KeyPath
)

if (-not (Test-Path $KeyPath)) {
    Write-Host "Error: File not found: $KeyPath" -ForegroundColor Red
    exit 1
}

try {
    $key = Get-Content $KeyPath -Raw
    $convertedKey = $key -replace "`r?`n", "\n"
    
    Write-Host "`n✅ Converted private key for .env file:`n" -ForegroundColor Green
    Write-Host "GITHUB_APP_PRIVATE_KEY=$convertedKey"
    Write-Host "`n📋 Copy the line above to your .env file`n" -ForegroundColor Cyan
} catch {
    Write-Host "Error reading key file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
