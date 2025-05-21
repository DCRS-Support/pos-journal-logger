# Run as Administrator

# Create directories
New-Item -ItemType Directory -Path "C:\pos-journal-logger\logs" -Force
New-Item -ItemType Directory -Path "C:\pos-journal-logger\scripts" -Force

# Install Chocolatey if not installed
if (-not (Get-Command choco.exe -ErrorAction SilentlyContinue)) {
    Write-Output "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    $env:Path += ";$env:ALLUSERSPROFILE\chocolatey\bin"
}

# Install curl via Chocolatey
choco install curl --force -y

# Download Python installer
$pythonInstaller = "C:\python.exe"
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe" -OutFile $pythonInstaller

# Install Python silently
Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait

# Delete the Python installer after installation
Remove-Item -Path $pythonInstaller -Force

# Refresh environment to get access to Python and pip
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)

# Download the Python script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/pos-journal-logger/pos-journal-logger.py" `
    -OutFile "C:\pos-journal-logger\scripts\pos-journal-logger.py"

# Download restart helper bat file
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/scripts/restart-journal-logger.bat" `
    -OutFile "C:\pos-journal-logger\scripts\restart-journal-logger.bat"

# Download shortcut to public desktop
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/CalebBrendel/pos-journal-logger/refs/heads/main/scripts/restart-journal-logger.lnk" `
    -OutFile "C:\Users\Public\Desktop\restart-journal-logger.lnk"

# Install pywin32
pip install pywin32

Start-Sleep -Seconds 10

# Register the Python script as a Windows service
python "C:\pos-journal-logger\scripts\pos-journal-logger.py" install

# Wait for service registration
Start-Sleep -Seconds 2

# Set the service to start automatically
Start-Process sc.exe -ArgumentList "config pos-journal-logger start= auto" -Wait

# Restart the computer
Restart-Computer -Force
