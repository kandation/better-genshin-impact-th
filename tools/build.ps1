# BetterGI Thai fork — build helper
# Local CLI builds may fail with wpftmp + CommunityToolkit duplicate generator errors.
# Use GitHub Actions publish workflow on the fork when local dotnet build fails.

param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Debug',
    [switch]$Publish
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot

# Prefer .NET 9 SDK if installed (newer Roslyn)
$dotnet9 = 'C:\dotnet9\dotnet.exe'
if (Test-Path $dotnet9) {
    $env:PATH = "C:\dotnet9;$env:PATH"
}

Write-Host "Using SDK: $(dotnet --version)"

dotnet restore BetterGenshinImpact.sln

if ($Publish) {
    dotnet publish BetterGenshinImpact/BetterGenshinImpact.csproj -c $Configuration -p:PublishProfile=FolderProfile
    $out = Join-Path $repoRoot "BetterGenshinImpact\bin\x64\$Configuration\net8.0-windows10.0.22621.0\publish\win-x64"
    Write-Host "Publish output: $out"
} else {
    dotnet build BetterGenshinImpact.sln -c $Configuration
    $out = Join-Path $repoRoot "BetterGenshinImpact\bin\x64\$Configuration\net8.0-windows10.0.22621.0"
    Write-Host "Build output: $out\BetterGI.exe"
}
