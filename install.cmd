@echo off
rem Windows wrapper. All logic lives in quintessence.py.
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 quintessence.py install %*
) else (
  python quintessence.py install %*
)
exit /b %errorlevel%
