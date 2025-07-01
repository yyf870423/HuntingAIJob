<#
Usage:
  .\daemon_process.ps1 start   # Start run.py as a daemon process, record PID to daemon_process.pid
  .\daemon_process.ps1 status  # Check if the process exists, return PID if running
  .\daemon_process.ps1 stop    # Stop the daemon process
#>
param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('start','status','stop','restart','help')]
    [string]$action
)

$pidFile = 'daemon_process.pid'

function Show-Help {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\daemon_process.ps1 start   # Start run.py as a daemon process, record PID to daemon_process.pid"
    Write-Host "  .\daemon_process.ps1 status  # Check if the process exists, return PID if running"
    Write-Host "  .\daemon_process.ps1 stop    # Stop the daemon process"
    Write-Host "  .\daemon_process.ps1 restart # Restart the daemon process"
}

function Start-RunPy {
    if (Test-Path $pidFile) {
        $runpyPid = Get-Content $pidFile
        if (Get-Process -Id $runpyPid -ErrorAction SilentlyContinue) {
            Write-Host "run.py is already running, PID: $runpyPid" -ForegroundColor Yellow
            return
        } else {
            Remove-Item $pidFile -Force
        }
    }
    # 检查并创建虚拟环境
    $venvCreated = $false
    if (-not (Test-Path .\venv\Scripts\Activate.ps1)) {
        Write-Host "Virtual environment not found, creating..." -ForegroundColor Yellow
        python -m venv venv
        $venvCreated = $true
    }
    . .\venv\Scripts\Activate.ps1
    if ($venvCreated) {
        Write-Host "Installing requirements..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
    $proc = Start-Process -FilePath python -ArgumentList '.\run.py' -WindowStyle Hidden -PassThru
    Set-Content -Path $pidFile -Value $proc.Id
    Write-Host "run.py started as a daemon process, PID: $($proc.Id), written to $pidFile" -ForegroundColor Green
}

function Status-RunPy {
    if (Test-Path $pidFile) {
        $runpyPid = Get-Content $pidFile
        $proc = Get-Process -Id $runpyPid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "run.py is running, PID: $runpyPid" -ForegroundColor Green
        } else {
            Write-Host "run.py is not running (pid file exists but process does not)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "run.py is not running (no pid file)" -ForegroundColor Yellow
    }
}

function Stop-RunPy {
    if (Test-Path $pidFile) {
        $runpyPid = Get-Content $pidFile
        $proc = Get-Process -Id $runpyPid -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $runpyPid -Force
            Write-Host "Stopped run.py daemon process (PID: $runpyPid)" -ForegroundColor Green
        } else {
            Write-Host "Process PID $runpyPid does not exist, nothing to stop." -ForegroundColor Yellow
        }
        Remove-Item $pidFile -Force
    } else {
        Write-Host "No pid file found, nothing to stop." -ForegroundColor Yellow
    }
}

switch ($action) {
    'start'  { Start-RunPy }
    'status' { Status-RunPy }
    'stop'   { Stop-RunPy }
    'restart' {
        Stop-RunPy
        Start-RunPy
    }
    'help'   { Show-Help }
    default  { Show-Help }
} 