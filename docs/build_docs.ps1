# Build the Sphinx HTML documentation from the repository root.
$ErrorActionPreference = 'Stop'
python -m sphinx -b html docs docs/_build/html
if ($LASTEXITCODE -ne 0) {
    throw 'Sphinx documentation build failed. Check the error output above.'
}
Write-Host 'Documentation built at docs\_build\html\index.html'
