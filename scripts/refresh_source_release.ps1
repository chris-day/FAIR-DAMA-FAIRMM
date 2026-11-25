$ErrorActionPreference='Stop'
$projectRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python=Join-Path $projectRoot '.venv/Scripts/python.exe'
Push-Location -LiteralPath $projectRoot
try {
    foreach($script in @('update_source_release.py','build_dimension_sankey.py','build_levels_sankey.py','document_source_refresh.py')) {
        & $python (Join-Path $PSScriptRoot $script)
        if($LASTEXITCODE -ne 0){throw ($script+' failed')}
    }
    & (Join-Path $PSScriptRoot 'build_ontology_all.ps1')
} finally { Pop-Location }
