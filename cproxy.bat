@echo off
SET mypath=%~dp0
SET "script=%mypath%\cproxy.py"
python --version >nul 2>nul (
	python %script% %*
) || (
	py %script% %*
)
