@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation.
REM Run from the docs\ folder, e.g. `make.bat html`. Output goes to _build\html.

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=python -m sphinx
)
if "%SPHINXOPTS%" == "" (
	set SPHINXOPTS=-W --keep-going
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% --version >NUL 2>NUL
if errorlevel 1 (
	echo.
	echo.Sphinx was not found. Activate the project virtual environment and
	echo.install the requirements, or run ..\build_docs.ps1, which does both.
	echo.
	popd
	exit /b 1
)

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
