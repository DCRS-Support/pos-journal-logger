@echo off

REM Creating directory to store POS Journal Logger...

mkdir C:\pos-journal-logger
mkdir C:\pos-journal-logger\logs
mkdir C:\pos-journal-logger\scripts

REM Installing Chocolately if not installed...

# @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

REM Installing curl if not installed...

choco install curl --force -y

REM Downloading Python 3.13.3...

curl -o "C:\python.exe" "https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe"

REM Installing Python 3.13.3...

C:\python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

REM Waiting for Windows to register Python environment variables...

timeout /t 10

REM Downloading the POS Journal Logger Python Script...

curl -o "C:\pos-journal-logger\scripts\pos-journal-logger.py" "https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/pos-journal-logger/pos-journal-logger.py"

REM Downloading the Restart POS Journal Logger bat file to restart the service from the Desktop...

curl -o "C:\pos-journal-logger\scripts\restart-journal-logger.bat" "https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/scripts/restart-journal-logger.bat"

REM Downloading the Restart POS Journal Logger shortcut and putting it in the Public Desktop Folder...

curl -o "C:\Users\Public\Desktop\restart-journal-logger.lnk" "https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/scripts/restart-journal-logger.lnk"

REM Installing the PyWin32 Package that can run Python scripts as a Windows service...

pip install pywin32

timeout /t 10

REM Register the POS Journal Logger Python Script as a Windows Service...

python C:\pos-journal-logger\scripts\pos-journal-logger.py install

REM Starting the POS Journal Logger Service...

python C:\pos-journal-logger\scripts\pos-journal-logger.py install

REM Waiting for Windows service to register...

timeout /t 2

REM Setting the POS Journal Logger service to be an Automatic service...

sc.exe config pos-journal-logger start= auto

REM Rebooting/Renaming PC to ensure service starts up automatically...

Rename-Computer -NewName "pos-journal-logger" -Restart
