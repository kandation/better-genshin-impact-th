# Patch an upstream BetterGI install to use Thai UI via th.json + config.
# Does NOT add "ไทย" to the settings dropdown (requires fork build).
param(
    [Parameter(Mandatory = $true)]
    [string]$BetterGiRoot,
    [string]$ThJsonSource = ""
)

if (-not $ThJsonSource) {
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    $ThJsonSource = (Resolve-Path (Join-Path $scriptDir "..\..\BetterGenshinImpact\User\I18n\th.json")).Path
}

$ErrorActionPreference = "Stop"

$configPath = Join-Path $BetterGiRoot "User\config.json"
$i18nDir = Join-Path $BetterGiRoot "User\I18n"
$thDest = Join-Path $i18nDir "th.json"

if (-not (Test-Path $configPath)) {
    throw "config.json not found: $configPath"
}
if (-not (Test-Path $ThJsonSource)) {
    throw "th.json source not found: $ThJsonSource"
}

New-Item -ItemType Directory -Force -Path $i18nDir | Out-Null
Copy-Item -Force $ThJsonSource $thDest

$config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $config.otherConfig) {
    throw "config.json missing otherConfig section"
}
$config.otherConfig.uiCultureInfoName = "th"
# Keep game OCR on Chinese client strings unless user plays EN client
# $config.otherConfig.gameCultureInfoName = "zh-Hans"

$json = $config | ConvertTo-Json -Depth 100
[System.IO.File]::WriteAllText($configPath, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host "Patched: $configPath (uiCultureInfoName=th)"
Write-Host "Copied:  $thDest"
Write-Host ""
Write-Host "Restart BetterGI. Thai will not appear in the language dropdown on upstream v0.62."
Write-Host "To change back, set otherConfig.uiCultureInfoName to en or zh-Hans in config.json."
