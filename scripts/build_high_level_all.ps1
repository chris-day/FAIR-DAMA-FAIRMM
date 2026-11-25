$ErrorActionPreference='Stop'
$projectRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Push-Location -LiteralPath $projectRoot
try {
    & .venv/Scripts/python.exe scripts/build_high_level_sankeys.py
    if($LASTEXITCODE -ne 0){throw 'High-level RDF extraction failed'}
    & scripts/render_high_level_sankeys.ps1
    & .venv/Scripts/python.exe -m zensical build --clean --strict
    if($LASTEXITCODE -ne 0){throw 'Strict documentation build failed'}
    & .venv/Scripts/python.exe scripts/validate_high_level_sankeys.py
    if($LASTEXITCODE -ne 0){throw 'High-level diagram validation failed'}
    node scripts/test_descriptor_tooltips.cjs
    if($LASTEXITCODE -ne 0){throw 'Descriptor tooltip component checks failed'}
} finally {Pop-Location}
