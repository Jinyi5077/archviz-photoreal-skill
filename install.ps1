[CmdletBinding()]
param([string]$DestinationRoot)
$ErrorActionPreference = 'Stop'

if (-not $DestinationRoot) {
    $DestinationRoot = if ($env:CODEX_HOME) {
        Join-Path $env:CODEX_HOME 'skills'
    } else {
        Join-Path $env:USERPROFILE '.codex\skills'
    }
}
$taskSource = Join-Path $PSScriptRoot 'skills\archviz-photoreal'
$taskDestination = [IO.Path]::GetFullPath((Join-Path $DestinationRoot 'archviz-photoreal'))
if (-not (Test-Path -LiteralPath (Join-Path $taskSource 'SKILL.md') -PathType Leaf)) {
    throw 'Source skill is incomplete: SKILL.md is missing.'
}
if (Test-Path -LiteralPath $taskDestination) {
    throw "Destination already exists; no files were overwritten: $taskDestination"
}
New-Item -ItemType Directory -Path $DestinationRoot -Force | Out-Null
Copy-Item -LiteralPath $taskSource -Destination $taskDestination -Recurse
foreach ($taskFile in (Get-ChildItem -LiteralPath $taskSource -File -Recurse)) {
    $taskRelative = $taskFile.FullName.Substring($taskSource.Length).TrimStart('\', '/')
    $taskCopy = Join-Path $taskDestination $taskRelative
    if ((Get-FileHash -LiteralPath $taskFile.FullName -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath $taskCopy -Algorithm SHA256).Hash) {
        throw "Installed file did not match source: $taskRelative"
    }
}
Write-Output "Installed: $taskDestination"
Write-Output 'The skill will be available on your next turn. Invoke it as $archviz-photoreal.'
