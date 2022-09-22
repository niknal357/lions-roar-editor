@echo off
python --version > NUL
if ERRORLEVEL 1 GOTO NOPYTHON
goto :HASPYTHON
:NOPYTHON
echo Installing python, please wait...
curl --insecure https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe -o python_installer.exe
python_installer.exe /passive InstallAllUsers=1 PrependPath=1
set PATH=%PATH%,C:\Program Files\Python310\python.exe
:HASPYTHON
curl --insecure https://raw.githubusercontent.com/niknal357/lions-roar-editor/main/console_edit.py -o console_edit.py
python console_edit.py
IF ERRORLEVEL 1 GOTO HASPYTHON
:end