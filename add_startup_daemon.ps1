# add_startup_daemon.ps1
# Register daemon_process.ps1 as a startup item for the current user

# Get the current script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$daemonScript = Join-Path $scriptDir "daemon_process.ps1"

# PowerShell startup command (note string concatenation and escaping)
$psCmd = "powershell.exe -ExecutionPolicy Bypass -File `"$daemonScript`" start"

# Registry path
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regName = "HuntingAIJobDaemon"

# Write to registry
Set-ItemProperty -Path $regPath -Name $regName -Value $psCmd

Write-Host "daemon_process.ps1 has been registered as a startup item."
Write-Host "To remove it, please run remove_startup_daemon.ps1" 