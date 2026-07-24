param(
    [string[]]$InputPath = @("tools/i18n/batches/th"),
    [string]$OutputDir = "tools/i18n/batches/th/done",
    [string]$Model = "models/gemini-3.6-flash",
    [int]$ChunkSize = 40,
    [switch]$DryRun,
    [switch]$Retranslate
)

$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $root

if (-not $env:GEMINI_API_KEY) {
    $envFile = Join-Path $PSScriptRoot ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^\s*([^#=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim().Trim('"').Trim("'")
                Set-Item -Path "env:$name" -Value $value
            }
        }
    }
}

if (-not $env:GEMINI_API_KEY) {
    Write-Error "Set GEMINI_API_KEY or create tools/i18n/.env"
}

$argsList = @(
    "tools/i18n/translate_gemini.py"
) + $InputPath + @(
    "--output-dir", $OutputDir,
    "--model", $Model,
    "--chunk-size", $ChunkSize
)
if ($DryRun) { $argsList += "--dry-run" }
if ($Retranslate) { $argsList += "--retranslate" }

python @argsList
