param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$RobotJar,
    [Parameter(Mandatory=$true)][string]$Java,
    [switch]$Acceptance,
    [string]$Workspace,
    [switch]$SyncSite
)
$ErrorActionPreference='Stop'
$component=Join-Path $PSScriptRoot '../integrated'
Push-Location -LiteralPath $component
try {
    & $Python scripts/pipeline.py --robot-jar $RobotJar --java $Java
    if($LASTEXITCODE -ne 0){throw 'Integrated pipeline failed'}
    if($Acceptance){
        if(-not $Workspace){throw 'Acceptance requires a fresh -Workspace outside the source directories'}
        $config=Get-Content release-config.json -Raw | ConvertFrom-Json
        $candidate=Join-Path (Get-Location) ('release/FAIR-DAMA-Integrated-'+$config.candidate_version+'.zip')
        $digest=(Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant()
        & $Python acceptance/run_acceptance.py --candidate $candidate --candidate-sha256 $digest --workspace $Workspace --robot-jar $RobotJar --java $Java
        if($LASTEXITCODE -ne 0){throw 'Integrated acceptance failed'}
    }
    if($SyncSite){
        & $Python scripts/sync_site.py
        if($LASTEXITCODE -ne 0){throw 'Site asset sync failed'}
    }
} finally {Pop-Location}
