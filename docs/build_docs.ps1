<#
.SYNOPSIS
    Build the Sphinx HTML documentation into docs\_build\html.

.DESCRIPTION
    Works from any folder and needs no manual setup:
      1. Finds Python 3.12 (py -3.12, then python, then python3).
      2. Creates the project virtual environment (.venv) if it is missing.
      3. Installs requirements.txt into .venv when packages are missing or
         requirements.txt has changed since the last install.
      4. Runs Sphinx with warnings treated as errors.
    A database server is not needed to build the documentation.

.PARAMETER Clean
    Delete the previous docs\_build output before building.

.PARAMETER Recreate
    Delete and recreate the .venv virtual environment before building.

.EXAMPLE
    .\build_docs.ps1
.EXAMPLE
    .\docs\build_docs.ps1 -Clean
#>
[CmdletBinding()]
param(
    [switch]$Clean,
    [switch]$Recreate
)

# Native tools (pip, Sphinx) write progress to stderr; Windows PowerShell 5.1
# would turn that into terminating errors under 'Stop', so exit codes are
# checked explicitly instead.
$ErrorActionPreference = 'Continue'
Set-StrictMode -Version 2.0

$DocsDir      = $PSScriptRoot
$ProjectRoot  = Split-Path -Parent $DocsDir
$VenvDir      = Join-Path $ProjectRoot '.venv'
# Standard Windows Python puts the interpreter in Scripts\; MSYS2/MinGW
# Python uses a POSIX-style bin\ folder. Both are supported.
$VenvPythonCandidates = @(
    (Join-Path $VenvDir 'Scripts\python.exe'),
    (Join-Path $VenvDir 'bin\python.exe'),
    (Join-Path $VenvDir 'bin\python3.exe')
)
$Requirements = Join-Path $ProjectRoot 'requirements.txt'
$StampFile    = Join-Path $VenvDir '.requirements.sha256'
$BuildDir     = Join-Path $DocsDir '_build'
$HtmlDir      = Join-Path $BuildDir 'html'
$DoctreeDir   = Join-Path $BuildDir 'doctrees'
$Wanted       = '3.12'

function Fail([string]$Message) {
    Write-Host ''
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

function Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-PythonVersion([string]$Exe, [string[]]$PrefixArgs) {
    # Returns e.g. '3.12', or $null if the command is missing or is the
    # Microsoft Store placeholder that only opens the Store.
    if (-not (Get-Command $Exe -ErrorAction SilentlyContinue)) { return $null }
    # No double quotes in the code: Windows PowerShell 5.1 strips them from
    # arguments passed to native programs.
    $code = "import sys; print(sys.version_info[0], sys.version_info[1], sep='.')"
    $out = & $Exe @PrefixArgs -c $code 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
    return ([string]($out | Select-Object -First 1)).Trim()
}

function Get-VenvPython {
    foreach ($p in $VenvPythonCandidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

function Find-Python {
    $candidates = @(
        @{ Exe = 'py';      Args = @("-$Wanted") },
        @{ Exe = 'python';  Args = @() },
        @{ Exe = 'python3'; Args = @() }
    )
    $fallback = $null
    foreach ($c in $candidates) {
        $ver = Get-PythonVersion $c.Exe $c.Args
        if (-not $ver) { continue }
        $c.Version = $ver
        if ($ver -eq $Wanted) { return $c }
        $parts = $ver.Split('.')
        if (-not $fallback -and [int]$parts[0] -eq 3 -and [int]$parts[1] -ge 10) {
            $fallback = $c
        }
    }
    return $fallback
}

Push-Location $ProjectRoot
try {
    if (-not (Test-Path $Requirements)) {
        Fail "requirements.txt was not found at $Requirements"
    }

    # --- 1-2. Virtual environment ------------------------------------------
    if ($Recreate -and (Test-Path $VenvDir)) {
        Step "Removing existing virtual environment ($VenvDir)"
        Remove-Item -Recurse -Force $VenvDir
    }

    $VenvPython = Get-VenvPython
    if ((Test-Path $VenvDir) -and -not $VenvPython) {
        Fail (".venv exists but contains no Windows Python interpreter (it may have " +
              "been created on another operating system). Run again with -Recreate.")
    }

    if (-not $VenvPython) {
        $python = Find-Python
        if (-not $python) {
            Fail ("Python $Wanted was not found. Install it from https://www.python.org/downloads/ " +
                  "(tick 'Add python.exe to PATH'), then run this script again.")
        }
        if ($python.Version -ne $Wanted) {
            Write-Warning "Python $Wanted not found; using Python $($python.Version) instead."
        }
        $shown = (@($python.Exe) + $python.Args) -join ' '
        Step "Creating virtual environment .venv with '$shown' (Python $($python.Version))"
        $venvArgs = @($python.Args) + @('-m', 'venv', $VenvDir)
        & $python.Exe @venvArgs
        $VenvPython = Get-VenvPython
        if ($LASTEXITCODE -ne 0 -or -not $VenvPython) {
            Fail 'Could not create the virtual environment.'
        }
    }

    $venvVersion = Get-PythonVersion $VenvPython @()
    if (-not $venvVersion) {
        Fail "The Python in .venv does not run. Run again with -Recreate."
    }
    Step "Using $VenvPython (Python $venvVersion)"

    # --- 3. Dependencies -----------------------------------------------------
    $reqHash = (Get-FileHash -Algorithm SHA256 $Requirements).Hash
    $stamp = $null
    if (Test-Path $StampFile) { $stamp = (Get-Content -Raw $StampFile).Trim() }

    & $VenvPython -c 'import sphinx, sphinx_rtd_theme, django, rest_framework, pymysql, requests' 2>$null
    $importsOk = ($LASTEXITCODE -eq 0)

    if (-not $importsOk -or $stamp -ne $reqHash) {
        Step 'Installing requirements.txt into .venv (first run can take a minute)'
        & $VenvPython -m pip install --disable-pip-version-check -r $Requirements
        if ($LASTEXITCODE -ne 0) {
            Fail 'pip could not install requirements.txt. Check your internet connection and the messages above.'
        }
        Set-Content -Path $StampFile -Value $reqHash -Encoding ascii
    } else {
        Step 'Requirements already installed'
    }

    # --- 4. Build ------------------------------------------------------------
    if ($Clean -and (Test-Path $BuildDir)) {
        Step 'Removing previous build output'
        foreach ($dir in @($HtmlDir, $DoctreeDir)) {
            if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
        }
    }

    Step 'Building HTML documentation with Sphinx'
    & $VenvPython -m sphinx -W --keep-going -b html -d $DoctreeDir $DocsDir $HtmlDir
    if ($LASTEXITCODE -ne 0) {
        Fail 'Sphinx reported errors or warnings (see above). The documentation was not fully built.'
    }

    $index = Join-Path $HtmlDir 'index.html'
    Write-Host ''
    Write-Host "Documentation built successfully: $index" -ForegroundColor Green
    Write-Host "Open it with:  start `"$index`""
    exit 0
}
finally {
    Pop-Location
}
