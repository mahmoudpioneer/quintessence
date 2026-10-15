@echo off
rem Windows wrapper. All logic lives in quintessence.py.
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 quintessence.py test %*
) else (
  python quintessence.py test %*
)
exit /b %errorlevel%
