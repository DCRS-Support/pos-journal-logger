@echo off

REM Creating directory to store POS Journal Logger...

mkdir C:\pos-journal-logger
mkdir C:\pos-journal-logger\logs
mkdir C:\pos-journal-logger\scripts

REM Installing Chocolately if not installed...

@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

REM Installing curl if not installed...

choco install curl --force -y

REM Downloading the Windows Part 2 Bat..will execute after installing Python so the new terminal session recognizes the environment variables added into Windows after the Python install

curl -o "C:\windows_p2.bat" "https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/scripts/windows_p2.bat"

REM Downloading Python 3.13.3...

curl -o "C:\python.exe" "https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe"

REM Installing Python 3.13.3...

C:\python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

REM Executing Windows Part 2 Bat file...

C:\windows_p2.bat
