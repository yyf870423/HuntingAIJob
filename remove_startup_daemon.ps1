# remove_startup_daemon.ps1
# Remove the startup item

$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regName = "HuntingAIJobDaemon"

Remove-ItemProperty -Path $regPath -Name $regName -ErrorAction SilentlyContinue

Write-Host "The startup item for daemon_process.ps1 has been removed." 