@echo off

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

REM Rebooting now...

shutdown /r /t 0
