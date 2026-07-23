# Scan BetterGI for missing translations.
# Usage:
#   .\tools\i18n\run-scan.ps1
#   .\tools\i18n\run-scan.ps1 -TargetLocale th
#   .\tools\i18n\run-scan.ps1 -TargetLocale en -IncludeEnglish

param(
    [string]$TargetLocale = "en",
    [switch]$IncludeEnglish
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Script = Join-Path $PSScriptRoot "scan_missing.py"

$args = @("--repo-root", $RepoRoot, "--target-locale", $TargetLocale)
if ($IncludeEnglish) {
    $args += "--include-english"
}

python $Script @args
