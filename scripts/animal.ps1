# ANIMAL — lanzador para Windows (PowerShell).
#
# Uso:
#   .\scripts\animal.ps1                  # TUI
#   .\scripts\animal.ps1 --demo --seed 42 # modo demo
#
# Usa uv si está en el PATH; en su defecto cae a `py -3.13 -m animal`.

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"

# Forzamos UTF-8 para que los acentos se vean bien.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        & uv run animal @Args
    }
    elseif (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.13 -m animal @Args
    }
    else {
        Write-Host "No encuentro ni uv ni py." -ForegroundColor Red
        Write-Host "Instala uv desde https://docs.astral.sh/uv/"
        Write-Host "o Python 3.13+ desde https://www.python.org/"
        exit 1
    }
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
