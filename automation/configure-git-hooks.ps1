# Run once per clone so commit-msg hooks in /githooks are used (strips unwanted trailers).
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot
& git config core.hooksPath githooks
Write-Host "Set core.hooksPath=githooks for $repoRoot"
