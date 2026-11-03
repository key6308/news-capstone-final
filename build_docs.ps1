<#
.SYNOPSIS
    Build the Sphinx documentation. Convenience wrapper for docs\build_docs.ps1.

.DESCRIPTION
    The documentation is already built in docs\_build\html; open
    docs\_build\html\index.html to read it. Run this script only to rebuild
    it. It creates .venv and installs requirements.txt automatically if needed.

.EXAMPLE
    .\build_docs.ps1
.EXAMPLE
    .\build_docs.ps1 -Clean
#>
[CmdletBinding()]
param(
    [switch]$Clean,
    [switch]$Recreate
)

& (Join-Path $PSScriptRoot 'docs\build_docs.ps1') @PSBoundParameters
exit $LASTEXITCODE
