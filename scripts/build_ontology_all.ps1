$ErrorActionPreference='Stop'
$projectRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python=Join-Path $projectRoot '.venv/Scripts/python.exe'
Push-Location -LiteralPath $projectRoot
try {
    foreach($script in @('build_fairmm_ontology.py','validate_fairmm_ontology.py','regenerate_sankeys_from_rdf.py','render_fairmm_ontology.py','document_fairmm_ontology.py')) {
        & $python (Join-Path $PSScriptRoot $script)
        if($LASTEXITCODE -ne 0){throw ($script+' failed')}
    }
    & (Join-Path $PSScriptRoot 'render_dimension_sankey.ps1')
    & (Join-Path $PSScriptRoot 'render_levels_sankey.ps1')
    & $python -m zensical build --clean --strict
    if($LASTEXITCODE -ne 0){throw 'Documentation build failed'}
    & $python (Join-Path $PSScriptRoot 'validate_levels_sankey.py')
    if($LASTEXITCODE -ne 0){throw 'Level diagram validation failed'}
    & $python (Join-Path $PSScriptRoot 'validate_fairmm_alignment.py') --fairmm ../FAIR-Maturity-Matrix --output results/executed --built-site
    if($LASTEXITCODE -ne 0){throw 'Existing crosswalk regression failed'}
    & $python (Join-Path $PSScriptRoot 'validate_source_release.py')
    if($LASTEXITCODE -ne 0){throw 'Supplied-source validation failed'}
} finally { Pop-Location }
